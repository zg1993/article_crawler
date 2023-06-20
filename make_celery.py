# -*- coding: utf-8 -*-

from flaskr import create_app

flask_app = create_app()
celery_app = flask_app.extensions['celery']
# flask_app.logger.info(celery_app)
