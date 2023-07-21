# -*- coding: utf-8 -*-

from flask import (Blueprint, request, current_app, jsonify, abort)
from flaskr.db import db
from .model import Article, Book, Task

from sqlalchemy import func
# from . import create_app

bp = Blueprint('task', __name__, url_prefix='/task')


@bp.route('/delete', methods=['POST'])
def delete_task():
    data = request.get_json()
    ids = data.get('id')
    current_app.logger.info(ids)
    with db.auto_commit_db():
        res = Task.query.filter(Task.id.in_(ids)).delete()
    if res != len(ids):
        response = {'code': 200, 'msg': '操作失败', 'success': False}
    else:
        response = {'code': 200, 'msg': '操作成功', 'success': True}
    return jsonify(response)


@bp.route('/add', methods=['POST'])
def add_task():
    data = request.get_json()
    task = Task(**data)
    res = True
    msg = '操作成功'
    try:
        with db.auto_commit_db():
            db.session.add(task)
    except Exception as e:
        res = False
        msg = e
    return {
        'code': 200,
        'resultCode': '',
        'msg': msg,
        'success': res,
    }


@bp.route('/update', methods=['POST'])
def update_task():
    data = request.get_json()
    # form = request.form
    ID = data['id']
    with db.auto_commit_db():
        res = Task.query.filter(Task.id == ID).update(data)
        print("res: {}".format(res))
    return {
        'code': 200,
        'resultCode': '',
        'msg': '操作成功',
        'success': True if res else False,
    }

@bp.route('/code-maps')
def get_code_maps_list():
    fields = [Task.name, Task.id]
    task_list = Task.query.with_entities(*fields).all()
    data = dict(task_list)
    response = {'code': 200, 'success': True, 'data': data}
    return jsonify(response)
    

@bp.route('/list', methods=['GET'])
def get_task_list():
    app_log = current_app.logger
    page = request.args.get('pageNo')
    per_page = request.args.get('pageSize')
    name = request.args.get('name', '')
    # a = Task.query.filter(Task.status == 1).all()
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
    # app_log.info(data)
    return {
        'code': 200,
        'resultCode': '',
        'msg': '操作成功',
        'success': True,
        'data': data
    }