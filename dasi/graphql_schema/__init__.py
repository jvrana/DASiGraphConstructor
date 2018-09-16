"""
graphql_schemas

GraphQL (via [Graphene](https://graphene-python.org/) provides central endpoints for the rest of the
application.

Here we attach the Query and Mutation endpoints to the schema. A single route (usually /graphql or /graphiql) provides the
endpoint.
"""

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField

from dasi.models import Sequence as SequenceModel
from dasi.graphql_schema.alignment import Alignments, AlignmentScores, SequenceRegions, createPrimerResults, createAlignment
from dasi.graphql_schema.primer import Primers, createPrimer
from dasi.graphql_schema.sequence import Sequences, Features, createSequence


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    # feature = SQLAlchemyConnectionField(Features)
    all_sequences = SQLAlchemyConnectionField(Sequences)
    all_alignments = SQLAlchemyConnectionField(Alignments)
    all_results = SQLAlchemyConnectionField(Alignments)
    all_primers = SQLAlchemyConnectionField(Primers)
    all_scores = SQLAlchemyConnectionField(AlignmentScores)
    sequences = graphene.List(Sequences)

    # define how to find certain models
    find_sequence = graphene.Field(lambda: Sequences, name=graphene.String())
    find_features = graphene.Field(lambda: Features, name=graphene.String(), seq_id=graphene.ID())

    alignments = graphene.String(query_name=graphene.String())

    def resolve_sequences(self, info):
        query = Sequences.get_query(info)
        seqs = query.all()
        return seqs

    def resolve_find_sequence(self, info, name):
        query = Sequences.get_query(info)
        # you can also use and_ with filter() eg: filter(and_(param1, param2)).first()
        return query.filter(SequenceModel.name == name).first()

    def resolve_alignments(self, info, query_name):
        schema = graphene.Schema(Query)
        seqs = schema.execute("""
        { allSequences {
            edges {
                node { 
                    id
                    name
                    bases
                    description
                    circular
                }
            }
        } }
        """)
        # edges = seqs['allSequences']['data']['edges']
        seqs = [x['node'] for x in seqs.data['allSequences']['edges']]

        find_query = """
            query findQuery($query_name: String!) {
                findSequence(name: $query_name) {
                    id
                    name
                    sequence
                    description
                    circular
                }
            }
        """

        query_seq = schema.execute(find_query, variable_values={"query_name": query_name})
        query_data = query_seq.data['findSequence']

        from pyblast import JSONBlast
        from marshmallow import ValidationError
        try:
            j = JSONBlast(seqs, query_data)
        except ValidationError as e:
            raise Exception("There was an error parsing the sequences.\n{}".format(e.messages))
        j.quick_blastn()
        print(j.results.alignments)


class Mutation(graphene.ObjectType):
    create_sequence = createSequence.Field(description="Creats a new sequence.")
    create_alignment = createAlignment.Field(description="Aligns sequences against a query. "
                                                     "If no subject_ids are provided, aligns query against all sequences "
                                                     "in the database.")
    create_primer = createPrimer.Field(description="Creates a new primer")
    create_primer_results = createPrimerResults.Field(description="Aligns primers against a query. "
                                                                  "If no primer_ids are provides, aligns query against "
                                                                  "all primers")



schema = graphene.Schema(query=Query, mutation=Mutation,
                         types=[Sequences, Features, AlignmentScores, SequenceRegions, Primers, Alignments])
