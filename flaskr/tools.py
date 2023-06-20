# -*- coding: utf-8 -*-
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles

from celery import Celery


class convert_timestamp_to_date(expression.FunctionElement):
    name = 'convert_timestamp_to_date'


@compiles(convert_timestamp_to_date)
def mysql_convert_timestamp_to_date(element, compiler, **kwargs):
    return 'from_unixtime({})'.format(compiler.process(element.clauses))


@compiles(convert_timestamp_to_date, 'sqlite')
def sqlite_convert_timestamp_to_date(element, compiler, **kwargs):
    return 'datetime({}, "unixepoch")'.format(compiler.process(element.clauses))

app = Celery('tasks', broker='redis://127.0.0.1:6379/0', backend='redis://127.0.0.1:6379/0')

@app.task
def hello():
    print('---')
    return 'hello world'

@app.task
def add(x, y):
    print('add')
    return x + y


if __name__ == '__main__':
    print('__main__')
