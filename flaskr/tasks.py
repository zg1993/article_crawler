# -*- coding: utf-8 -*-
from celery import Celery



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
