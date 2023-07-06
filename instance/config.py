# -*- coding: utf-8 -*-

from celery.schedules import crontab
from urllib.parse import quote

SECRET_KEY = 'pro'

# database config
database_config = {
    'name': 'root',
    'passwd': 'sgit@123',
    'host': '172.25.0.25',
    'port': 3306,
    'database': 'crawler',
}

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{name}:{passwd}@{host}:{port}/{database}'.format(
    **database_config)
SQLALCHEMY_COMMIT_ON_TEARDOWN = True

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 10
# REDIS_PASSWD = quote('sjzy#1111')

CELERY = dict(
    broker_url="redis://{}:{}/{}".format(REDIS_HOST,REDIS_PORT,REDIS_DB),
    result_backend="redis://{}:{}/{}".format(REDIS_HOST,REDIS_PORT,REDIS_DB),
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
        # 'test': {
        #     'task': 'weixin',
        #     # 'schedule': crontab(minute="*/1")
        #     'schedule': crontab(minute=59, hour=8)
        # }
    })
