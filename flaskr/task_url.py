# -*- coding: utf-8 -*-

import functools

from flask import (Blueprint, flash, g, redirect, request, session, url_for,
                   current_app, jsonify)
from flaskr.db import db
from .model import Article, Book, Task
from sqlalchemy import func
import json
from . import tasks
from celery.result import AsyncResult


bp = Blueprint('task', __name__, url_prefix='/task')

@bp.route('/start_now')
def start_now():
    res =  tasks.weixin.delay()
    return {'code': 200, 'res': res.id}

@bp.route('/redis')
def get_dbsize():
    redis_cli = current_app.extensions['redis']
    return {'code': 200, 'res': redis_cli.dbsize()}

@bp.route('/update', methods=['POST'])
def update_task():
    data = request.get_json()
    print(data)
    # form = request.form
    ID = data['id']
    with db.auto_commit_db():
        res = Task.query.filter(Task.id == ID).update(data)
        print("res: {}".format(res))
    return {'code': 200, 'res': 'success' if res else 'id not existed'}

@bp.route('/list', methods=['GET'])
def get_task_list():
    app_log = current_app.logger
    page = request.args.get('pageNo')
    per_page = request.args.get('pageSize')
    name = request.args.get('name', '')

    a = Task.query.filter(Task.status==1).all()
    print([i.to_json() for i in a])

    # current_app.logger.info(res)
    art_query = Task.query.filter(
        Task.name.like("%" + name + "%") if name is not None else "")
    art_page_data = art_query.paginate(page=int(page), per_page=int(per_page))
    data = {
        'current': art_page_data.page,
        'pages': art_page_data.pages,
        'size': art_page_data.per_page,
        'total': art_page_data.total,
        'records': [item.to_json() for item in art_page_data.items]
    }
    return {
        'code': 200,
        'resultCode': '',
        'msg': '操作成功',
        'success': True,
        'data': data
    }

# @bp.route('/<string:aid>', methods=['GET'])
# def get_article_detail(aid):
#     app_log = current_app.logger
#     art = Article.query.get(aid)  # aid not exists None
#     data = {}
#     if art:
#         data = art.to_json()
#         data['content'] = art.content
#     return {'code': 200, 'data': data, 'success': True}


@bp.route('/add')
def add_article():
    current_app.logger.info(request)
    article = Article(
        aid='2674775906_3',
        title='渤海银行关于调整人民币存款挂牌利率的公告2',
        link=
        'http://mp.weixin.qq.com/s?__biz=MjM5NDM5ODUzNQ==&mid=2674775906&idx=1&sn=6d978316a3c0b49efc21402197c97e49&chksm=bc111f4a8b66965c477bd50b62a9304280e8361a7ba93ab004d59328df74b51129b75902d36f#rd',
        cover=
        'https://mmbiz.qlogo.cn/mmbiz_jpg/CicWTKtA8bDay2yAfuwlzc89mn2UIlGoYHzrhUad8prAXPR7oianAsSxyzgfwUbaFEZU9dlusC8TIaCZDDhJicy7A/0?wx_fmt=jpeg',
        content='<h1><h1>',
        update_time=1687136155
        # update_time = mysql_convert_timestamp_to_date(1687136155),
    )
    print('article: ', article)
    # r = db.session.query(Article.aid, Article.update_time).all()
    current_app.logger.info(dir(Article.aid))
    r = db.session.query(Article.aid, Article.content,
                         func.unix_timestamp(Article.update_time)).all()
    # r = db.session.query(Article.aid, func.from_unixtime((Article.update_time), "%Y-%m-%d %H:%i:%s")).all()
    res = []
    import time, datetime
    for i in r:
        current_app.logger.info(i)
    for aid, content, update_time in r:
        # current_app.logger.info('aid: {}'.format(aid))
        # current_app.logger.info('update_time: {}'.format(update_time))
        # i.update_time = int(time.mktime(i.update_time.timetuple()))
        # d = dict(i)
        d = dict(update_time=update_time, content=content, aid=aid)
        # d['update_time'] = int(time.mktime(d['update_time'].timetuple()))
        res.append(d)
        # current_app.logger.info(dict(i))
    # current_app.logger.info(r)
    db.session.add(article)
    db.session.commit()

    return res
    # return {'code':200, 'data':1}
