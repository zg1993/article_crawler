# -*- coding: utf-8 -*-

import os

from flask import Flask

from logging.config import dictConfig


def create_app(test_config=None):
    # create and configure the app
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format':
                '[%(asctime)s %(levelname)s in %(module)s.py, line %(lineno)s]: %(message)s',
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    # @app.route('/hello')
    # def hello():
    #     return 'Hello, World!'
    print('create_app', app)
    from . import db
    db.init(app)
    #导入注册路由
    from . import article_url
    app.register_blueprint(article_url.bp)

    return app