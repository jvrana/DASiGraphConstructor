import graphene
from graphene import relay

from dasi.database import get_session
from dasi.models import Primer
from dasi.graphql_schema.base import ActiveSQLAlchemyObjectType


class Primers(ActiveSQLAlchemyObjectType):
    class Meta:
        model = Primer
        interfaces = (relay.Node,)


class PrimerInput(graphene.InputObjectType):
    name = graphene.String(required=True, description="name of the primer")
    bases = graphene.String(required=True, description="bases of the primer")


class createPrimer(graphene.Mutation):
    class Arguments:
        primer = PrimerInput(required=True)

    ok = graphene.Boolean()
    primer = graphene.Field(Primers)

    @staticmethod
    def mutate(root, info, primer):
        db_session = get_session()
        primer = Primer(name=primer.name, bases=primer.bases)
        db_session.add(primer)
        db_session.commit()
        ok = True
        return createPrimer(ok=ok, primer=primer)


