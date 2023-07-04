# -*- coding: utf-8 -*-

import os

from flask import Flask
from celery import Celery, Task
from celery.schedules import crontab

from logging.config import dictConfig
import redis


def create_app(test_config=None) -> Flask:
    # create and configure the app
    if not test_config:
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
        })  # setting logs
    app = Flask(__name__, instance_relative_config=True)
    if app.config['DEBUG'] or test_config:
        app.config.from_pyfile('dev_config.py')
    else:
        app.config.from_pyfile('config.py')
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # init celery redis 初始化配置
    app.config.from_mapping(CELERY=dict(
        broker_url="redis://localhost",
        result_backend="redis://localhost",
        timezone='Asia/Shanghai',  # 设置东八区
        enable_utc=False,  # 设置东八区
        broker_connection_retry_on_startup=True,
        beat_schedule={
            # 'add':{
            #     'task': 'flaskr.tasks.add',
            #     'schedule': crontab(minute=27, hour=15),
            #     'args': (0, 100)
            # },
            #  'my_task':{
            #     'task': 'my_task',
            #     'schedule': 3,
            # },
            'weixin': {
                'task': 'weixin',
                'schedule': crontab(minute=50, hour=23),
                # 'schedule': crontab(minute="*/1"),
                # 'schedule': 60,
            },
            'test': {
                'task': 'weixin',
                # 'schedule': crontab(minute="*/1")
                'schedule': crontab(minute=59, hour=8)
            }
        }))
    celery_init_app(app)

    # a simple page that says hello
    # @app.route('/hello')
    # def hello():
    #     return 'Hello, World!'
    # print('create_app', app)
    from . import db
    db.init(app)

    #导入注册路由
    from . import article_url, task_url
    app.register_blueprint(article_url.bp)
    app.register_blueprint(task_url.bp)

    # store redis-cli
    app.extensions['redis'] = redis.Redis(
        host=app.config.get('REDIS_HOST', 'localhost'),
        port=app.config.get('REDIS_PORT', 6379),
        decode_responses=True
        )
    return app


def celery_init_app(app: Flask) -> Celery:

    class FalskTask(Task):

        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    # app.logger.info(app.name)
    celery_app = Celery(app.name, task_cls=FalskTask)
    # app.logger.info(app.config['CELERY'])
    celery_app.config_from_object(app.config['CELERY'])
    celery_app.set_default()
    app.extensions['celery'] = celery_app
    return celery_app