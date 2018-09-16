from graphene_sqlalchemy import SQLAlchemyObjectType


class ActiveSQLAlchemyObjectType(SQLAlchemyObjectType):
    class Meta:
        abstract = True