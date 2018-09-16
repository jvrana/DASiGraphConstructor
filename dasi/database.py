from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import current_app, g

# Replace 'sqlite:///rfg.db' with your path to database
# engine = create_engine('sqlite:///rfg.db', convert_unicode=True)
# db_session = scoped_session(sessionmaker(autocommit=False,
#                                          autoflush=False,
#                                          bind=engine))
# Base = declarative_base()
# Base.query = db_session.query_property()


def get_engine():
    if 'engine' not in g:
        config = current_app.config
        g.engine = create_engine(
            current_app.config['DATABASE'],
            convert_unicode=True
        )
    return g.engine


def get_session():
    """Returns the database session"""
    if 'session' not in g:
        g.session = scoped_session(sessionmaker(autocommit=False,
                                    autoflush=False,
                                    bind=get_engine()))
    return g.session


def close_session(e=None):
    """Closes the database session"""
    db = g.pop('session', None)

    if db is not None:
        db.close()


def get_db():
    return g.db


def init_app(app):
    app.teardown_appcontext(close_session)
    with app.app_context():
        Model.Base.query = get_session().query_property()
        Model.Base.metadata.create_all(get_engine())


class Model(object):
    Base = declarative_base()
