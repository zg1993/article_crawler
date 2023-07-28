# -*- coding: utf-8 -*-

import functools

from flask import (Blueprint, redirect, request, session, url_for, current_app,
                   jsonify)
from flaskr.db import db
from .model import Article, Book, Task, Test
from sqlalchemy import func
import asyncio
from common.const import SNUID_KEY, TASK_SET_KEY

bp = Blueprint('func', __name__, url_prefix='/func')


COOKEIS_KEY = 'crawler:cookies'


@bp.route('/start_now_task', methods=['POST'])
def start_now_task():
    from crawler.article import execute_task
    data = request.get_json()
    redis_cli = current_app.extensions['redis']
    ID = data.get('id')
    current_app.logger.info(redis_cli.sismember(TASK_SET_KEY, ID))
    if redis_cli.sismember(TASK_SET_KEY, ID) is True:
        response = {'code': 200, 'success': False, 'msg': '任务正在执行，请勿重复操作'}
    else:
        redis_cli.sadd(TASK_SET_KEY, ID)
        data['execute_status'] = 0
        with db.auto_commit_db():
            res = Task.query.filter(Task.id == ID).update(data)
        response = {'code': 200, 'success': True if res else False}
    return jsonify(response)


@bp.route("/update_cookies", methods=['POST'])
def update_cookies():
    try:
        redis_cli = current_app.extensions['redis']
        data = request.get_json()
        res = redis_cli.set(COOKEIS_KEY, data['cookies'])
        code = 200 if res is True else 500
        return {
            'code': code,
            'data': redis_cli.get(COOKEIS_KEY),
            'success': True
        }
    except Exception as e:
        return {'code': 500, 'res': e}


@bp.route('/update_snuid', methods=['POST'])
def update_snuid():
    try:
        redis_cli = current_app.extensions['redis']
        data = request.get_json()
        res = redis_cli.set(SNUID_KEY, data['snuid'])
        code = 200 if res is True else 500
        return {
            'code': code,
            'data': redis_cli.get(SNUID_KEY),
            'success': True
        }
    except Exception as e:
        return {'code': 500, 'res': e}


@bp.route('/check_cookies')
def check_cookies():
    from crawler.article import get_token1, cal_date_cookies
    try:
        redis_cli = current_app.extensions['redis']
        res = get_token1(redis_cli)
        date = cal_date_cookies(redis_cli)
        return jsonify({
            'code': 200,
            'data': {
                'isValid': True if res else False,
                'updateTime': date
            },
            'success': True
        })
    except Exception as e:
        return jsonify({'code': 500, 'res': e})


@bp.route('/start_now')
def start_now():
    # fields = [Test.title, func.unix_timestamp(Test.tsp), func.date_format(Test.delete_time,'%Y-%m-%d %H:%i:%s')]
    res = Test.query.filter().all()
    
    # res = tasks.weixin.delay()
    current_app.logger.info(res)
    # current_app.logger.info(dict(res))
    return {'code': 200, 'res': [item.to_json() for item in res]}
    # return {'code': 200, 'res': res}


@bp.route('/start_now_')
def start_now_():

    t = Test(update_time=1234,
             title='第2',
             tsp='2021-02-04 03:14:31',
             content='内容',
             js=['l0'],
             delete_time='2023-07-27 11:14:31')
    with db.auto_commit_db():
        db.session.add(t)
        pass
    # res = tasks.weixin.delay()
    return {'code': 200, 'res': 'rr'}


# @bp.route('/redis')
def get_dbsize():
    redis_cli = current_app.extensions['redis']
    return {'code': 200, 'res': redis_cli.dbsize()}
