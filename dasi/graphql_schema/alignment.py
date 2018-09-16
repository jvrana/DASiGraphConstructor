import graphene
from graphene import relay

from dasi.database import get_session
from dasi.models import Alignment, SequenceRegion, AlignmentScore, Primer
from dasi.graphql_schema.base import ActiveSQLAlchemyObjectType
from dasi.graphql_schema.sequence import Sequences
from dasi.graphql_schema.primer import Primers
from pyblast import JSONBlast


class SequenceRegions(ActiveSQLAlchemyObjectType):
    class Meta:
        model = SequenceRegion
        interfaces = (relay.Node,)


class Alignments(ActiveSQLAlchemyObjectType):
    class Meta:
        model = Alignment
        interfaces = (relay.Node,)


class AlignmentScores(ActiveSQLAlchemyObjectType):
    class Meta:
        model = AlignmentScore
        interfaces = (relay.Node,)


class createAlignment(graphene.Mutation):
    """
    Utilizes a JSONBlast to find perfect alignments between a query and subjects.

    If subject_ids are not provided, the query will be aligned to the entire database.
    """
    class Arguments:
        subject_ids = graphene.List(graphene.ID)
        query_id = graphene.ID(required=True)

    ok = graphene.Boolean()
    results = graphene.List(Alignments)

    @staticmethod
    def mutate(root, info, query_id, subject_ids=None):

        # pass
        # if subject_ids is None:
        #     subject_ids = graphene.Node.

        db_session = get_session()
        query_seq = graphene.Node.get_node_from_global_id(info, query_id)

        if subject_ids is None:
            query = Sequences.get_query(info)
            subjects = query.all()
            subjects = [s for s in subjects if s.id != query_seq.id]
        else:
            subjects = [graphene.Node.get_node_from_global_id(info, sid) for sid in subject_ids]

        j = JSONBlast(subjects, query_seq, preloaded=True, span_origin=True, gapopen=3, gapextend=3, penalty=-5, reward=1)
        j.quick_blastn()

        alignments = j.results.get_perfect().alignments

        ok = False
        results = []
        if alignments is not None:
            ok = True
            for align in alignments:
                score = AlignmentScore(**align['meta'])
                query_align = SequenceRegion(**align['query'])
                subject_align = SequenceRegion(**align['subject'])
                db_session.add(query_align)
                db_session.add(subject_align)
                db_session.add(score)
                result = Alignment(alignment_score=score, query=query_align, subject=subject_align)
                db_session.add(result)
                db_session.commit()
                results.append(result)
        return createAlignment(ok=ok, results=results)


class createPrimerResults(graphene.Mutation):
    class Arguments:
        primer_ids = graphene.List(graphene.ID)
        query_id = graphene.ID(required=True)

    ok = graphene.Boolean()
    results = graphene.List(Alignments)

    @staticmethod
    def mutate(root, info, query_id, primer_ids=None):

        # pass
        # if subject_ids is None:
        #     subject_ids = graphene.Node.

        db_session = get_session()
        query_seq = graphene.Node.get_node_from_global_id(info, query_id)
        primers = []
        if primer_ids is None:
            query = Primers.get_query(info)
            primers = query.all()
        else:
            primers = [graphene.Node.get_node_from_global_id(info, pid) for pid in primer_ids]

        for p in primers:
            p.circular = False

        j = JSONBlast(primers, query_seq, preloaded=True, span_origin=False, gapopen=3, gapextend=3, penalty=-5, reward=1)
        j.quick_blastn_short()

        alignments = j.results.get_with_perfect_subjects().get_perfect().alignments

        ok = False
        results = []
        if alignments is not None:
            ok = True
            for align in alignments:
                score = AlignmentScore(**align['meta'])
                query_align = SequenceRegion(**align['query'])
                subject_align = SequenceRegion(**align['subject'])
                db_session.add(query_align)
                db_session.add(subject_align)
                db_session.add(score)
                result = Alignment(alignment_score=score, query=query_align, subject=subject_align)
                db_session.add(result)
                db_session.commit()
                results.append(result)
        return createPrimerResults(ok=ok, results=results)
