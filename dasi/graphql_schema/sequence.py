import graphene
from graphene import relay

from dasi.database import get_session
from dasi.models import Sequence, Feature
from dasi.graphql_schema.base import ActiveSQLAlchemyObjectType


class Sequences(ActiveSQLAlchemyObjectType):
    class Meta:
        model = Sequence
        interfaces = (relay.Node,)


class Features(ActiveSQLAlchemyObjectType):
    class Meta:
        model = Feature
        interfaces = (relay.Node,)


# TODO: make strand an Enum graphene type?
class FeatureInput(graphene.InputObjectType):
    """A sequence feature input"""
    name = graphene.String(required=True, description="feature name")
    type = graphene.String(required=True, description="type of feature")
    start = graphene.Int(required=True, description="start of the feature (index starts at 1)")
    end = graphene.Int(required=True, description="end of the feature (index ends at length)")
    strand = graphene.Int(required=True, description="1 for forward, -1 for reverse")
    id = graphene.ID()


class SequenceInput(graphene.InputObjectType):
    name = graphene.String(required=True, description="name of the sequence")
    bases = graphene.String(required=True, description="bases of the sequence")
    circular = graphene.Boolean(required=True, description="whether this DNA is circular or not")
    description = graphene.String(description="descriptive text of this DNA")
    features = graphene.List(FeatureInput, description="annotations of this DNA", default=[])


# Used to Create New User
class createSequence(graphene.Mutation):
    class Arguments:
        sequence = SequenceInput(required=True)

    ok = graphene.Boolean()
    sequence = graphene.Field(Sequences)

    @staticmethod
    def mutate(root, info, sequence):
        db_session = get_session()
        seq = Sequence(
            name=sequence.name,
            bases=sequence.bases,
            circular=sequence.circular,
            description=sequence.description,
            size=len(sequence.bases)
        )
        for feature in sequence.features:
            seq.features.append(Feature(**feature))
        db_session.add(seq)
        db_session.commit()
        ok = True
        return createSequence(sequence=seq, ok=ok)

