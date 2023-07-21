# -*- coding: utf-8 -*-

import functools

from flask import (Blueprint, redirect, request, session, url_for,
                   current_app, jsonify )
from flaskr.db import db
from .model import Article, Book, Task
from sqlalchemy import func


bp = Blueprint('func', __name__, url_prefix='/func')

COOKEIS_KEY = 'crawler:cookies'

@bp.route("/update_cookies", methods=['POST'])
def update_cookies():
    try:
        redis_cli = current_app.extensions['redis']
        data = request.get_json()
        res = redis_cli.set(COOKEIS_KEY, data['cookies'])
        code = 200 if res is True else 500
        return {'code': code, 'data': redis_cli.get(COOKEIS_KEY), 'success': True}
    except Exception as e:
        return {'code': 500, 'res': e}

@bp.route('/check_cookies')
def check_cookies():
    from crawler.article import get_token1
    try:
        redis_cli = current_app.extensions['redis']
        res = get_token1(redis_cli)
        current_app.logger.info(res)
        return jsonify({'code': 200, 'data': '有效' if res else '已失效', 'success': True})
    except Exception as e:
        return jsonify({'code': 500, 'res': e})

@bp.route('/start_now')
def start_now():
    pass
    # res = tasks.weixin.delay()
    # return {'code': 200, 'res': res.id}


@bp.route('/redis')
def get_dbsize():
    redis_cli = current_app.extensions['redis']
    return {'code': 200, 'res': redis_cli.dbsize()}
