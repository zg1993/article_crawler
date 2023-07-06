# -*- coding: utf-8 -*-

from flaskr import create_app
# from flaskr import tasks
import os

if 'dev' == os.environ.get('CELERY_CONFIG_MODULE'):
    flask_app = create_app(True)
else:
    flask_app = create_app()
celery_app = flask_app.extensions['celery']
# flask_app.logger.info(celery_app)
# flask_app.logger.info(dir(celery_app))
# flask_app.logger.info(celery_app.timezone)
# flask_app.logger.info(celery_app.uses_utc_timezone())

# @celery_app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(10, tasks.my_task.s())
