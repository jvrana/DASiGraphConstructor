# flask_sqlalchemy/app.py
import os
from flask import Flask, g
from flask_graphql import GraphQLView
# from .database import db_session
from dasi.database import init_app
from dasi.graphql_schema import schema


def create_app(env_variables=None, config='config.Development'):
    app = Flask(__name__, instance_relative_config=True, template_folder="templates")
    app.config.from_object(config)
    try:
        app.config.from_object(os.environ["SETTINGS"])
    except:
        pass
    if env_variables is not None:
        app.config.update(env_variables)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    print(app.config)

    # apply the blueprints to the app
    from dasi import blueprints
    app.register_blueprint(blueprints.root.bp)
    app.register_blueprint(blueprints.sequences.bp)


    # single url for api
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True,
            context={},
            root=4,
        )
    )

    @app.teardown_appcontext
    def teardown_session(exception=None):
        session = g.pop('session', None)

        if session is not None:
            session.close()
    init_app(app)

    return app