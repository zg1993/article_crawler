# -*- coding: utf-8 -*-

import functools

from flask import (Blueprint, flash, g, redirect, request, session, url_for,
                   current_app, jsonify)
from flaskr.db import db
from .model import Article, Task
from sqlalchemy import func
import json
from . import tasks
from celery.result import AsyncResult
from crawler.utils import str_to_timestamp
import re


bp = Blueprint('article', __name__, url_prefix='/article')

pattern = re.compile(r'<[^<>]+>')
patternSpace = re.compile(r'[\s+|\n]')


@bp.route("/result/<id>")
def result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    ready = result.ready()
    return {
        "ready": ready,
        "successful": result.successful() if ready else None,
        "value": result.get() if ready else result.result,
    }

@bp.route('/update', methods=['POST'])
def update_article():
    data = request.get_json()
    ID: str = data.pop('id')
    current_app.logger.info(ID)
    with db.auto_commit_db():
        # res = Article.query.filter(Article.aid == ID).update(data)
        res = Article.query.filter(Article.aid == ID).update(data)
        current_app.logger.info(res)
    return {
        'code': 200,
        'resultCode': '',
        'msg': '操作成功',
        'success': True if res else False,
    }


@bp.route('/delete', methods=['POST'])
def delete_article():
    data = request.get_json()
    ids = data.get('id')
    with db.auto_commit_db():
        res = Article.query.filter(Article.aid.in_(ids)).delete()
    if res != len(ids):
        response = {'code': 200, 'msg': '操作失败', 'success': False}
    else:
        response = {'code': 200, 'msg': '操作成功', 'success': True}
    return jsonify(response)

@bp.route('/<string:aid>', methods=['GET'])
def get_article_detail(aid):
    app_log = current_app.logger
    art = Article.query.get(aid)  # aid not exists None
    data = {}
    if art:
        data = art.to_json()
        data['content'] = art.content
    return {'code': 200, 'data': data, 'success': True}


@bp.route('/list', methods=['GET'])
def get_article_list():
    app_log = current_app.logger
    page = request.args.get('pageNo')
    per_page = request.args.get('pageSize')
    title = request.args.get('title', '')
    topic = request.args.get('topic')
    timeBegin = request.args.get('timeBegin')
    timeEnd = request.args.get('timeEnd')
    filters = []
    if topic is not None:
        filters.append(Article.topic == topic)
    if timeBegin and timeEnd:
        timestampBegin = str_to_timestamp(timeBegin)
        timestampEnd = str_to_timestamp(timeEnd)
        filters.append(Article.update_time.between(timestampBegin, timestampEnd))
    fileds = [Article.aid, Article.content, Article.extracted_from, Article.title, Article.cover, Article.link, Article.update_time, Task.name.label('topic')]
    art_query = Article.query.filter(*filters).join(Task, Article.topic == Task.id).filter(
        Article.title.like("%" + title + "%") if title is not None else "").with_entities(*fileds).order_by(Article.update_time.desc())
    # art_query = Article.query.filter(
    #     Article.title.like("%" + title + "%") if title is not None else "").order_by(Article.update_time.desc())
    art_page_data = art_query.paginate(page=int(page), per_page=int(per_page))
    records = []
    for item in art_page_data.items:
        record = item._asdict()
        record['update_time'] = record['update_time'] * 1000
        content = record.pop('content')
        # content = record.get('content')
        if content:
            # current_app.logger.info(len(content))
            record['text_content'] = patternSpace.sub('',pattern.sub('', content))[:400]
            # app_log.info(len(record['text_content']))
        records.append(record)
    
    data = {
        'current': art_page_data.page,
        'pages': art_page_data.pages,
        'size': art_page_data.per_page,
        'total': art_page_data.total,
        'records': records
    }
    return jsonify({
        'code': 200,
        'resultCode': '',
        'msg': '操作成功',
        'success': True,
        'data': data
    })


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
