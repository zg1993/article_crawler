# -*- coding: utf-8 -*-

import functools

from flask import (Blueprint, redirect, request, session, url_for,
                   current_app )
from flaskr.db import db
from .model import Article, Book, Task
from sqlalchemy import func


bp = Blueprint('func', __name__, url_prefix='/func')

COOKEIS_KEY = 'crawler:cookies'

@bp.route("/update_cookies", methods=['POST'])
def update_cookies():
    try:
        redis_cli = current_app.extensions['redis']
        res = redis_cli.set(COOKEIS_KEY, request.form['cookies'])
        code = 200 if res is True else 500
        return {'code': code, 'res': redis_cli.get(COOKEIS_KEY)}
    except Exception as e:
        return {'code': 500, 'res': e}

@bp.route('/start_now')
def start_now():
    pass
    # res = tasks.weixin.delay()
    # return {'code': 200, 'res': res.id}


@bp.route('/redis')
def get_dbsize():
    redis_cli = current_app.extensions['redis']
    return {'code': 200, 'res': redis_cli.dbsize()}
