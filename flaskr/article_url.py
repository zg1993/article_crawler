# -*- coding: utf-8 -*-

import functools

from flask import (
    Blueprint, flash, g, redirect, request, session, url_for, current_app, jsonify
)
from flaskr.db import db
from .model import Article,Book
from sqlalchemy import func
import json

bp = Blueprint('article', __name__, url_prefix='/article')

@bp.route('/add')
def add_article():
    current_app.logger.info(request)
    article = Article(
        aid = '2674775906_3',
        title = '渤海银行关于调整人民币存款挂牌利率的公告2',
        link = 'http://mp.weixin.qq.com/s?__biz=MjM5NDM5ODUzNQ==&mid=2674775906&idx=1&sn=6d978316a3c0b49efc21402197c97e49&chksm=bc111f4a8b66965c477bd50b62a9304280e8361a7ba93ab004d59328df74b51129b75902d36f#rd',
        cover = 'https://mmbiz.qlogo.cn/mmbiz_jpg/CicWTKtA8bDay2yAfuwlzc89mn2UIlGoYHzrhUad8prAXPR7oianAsSxyzgfwUbaFEZU9dlusC8TIaCZDDhJicy7A/0?wx_fmt=jpeg',
        content='<h1><h1>'
        # update_time = func.from_unixtime(1687136155)
        # update_time = mysql_convert_timestamp_to_date(1687136155),
    )
    # r = db.session.query(Article.aid, Article.update_time).all()
    current_app.logger.info(dir(Article.aid))
    r = db.session.query(Article.aid, Article.content ,func.unix_timestamp(Article.update_time)).all()
    # r = db.session.query(Article.aid, func.from_unixtime((Article.update_time), "%Y-%m-%d %H:%i:%s")).all()
    res = []
    # current_app.logger.info(func.from_unixtime(1687136155))
    # current_app.logger.info(func.unix_timestamp)
    # current_app.logger.info(type(r[0]))
    # current_app.logger.info(dict(r[0]))
    # current_app.logger.info(dir(r[0]))
    current_app.logger.info(r[0]._fields)
    current_app.logger.info(r[0].keys())
    import time, datetime
    for i in r:
        current_app.logger.info(i)
    for aid, content ,update_time in r:
        # current_app.logger.info('aid: {}'.format(aid))
        # current_app.logger.info('update_time: {}'.format(update_time))
        # i.update_time = int(time.mktime(i.update_time.timetuple()))
        # d = dict(i)
        d = dict(update_time=update_time, content=content, aid=aid)
        # d['update_time'] = int(time.mktime(d['update_time'].timetuple()))
        res.append(d)
        # current_app.logger.info(dict(i))
    # current_app.logger.info(r)
    # db.session.add(article)
    # db.session.commit()
    
    return res
    # return {'code':200, 'data':1}
    


