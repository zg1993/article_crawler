# -*- coding: utf-8 -*-
from celery import shared_task, Task
import time
from .model import Article, Book
from .db import db
from flask import current_app

import random
import asyncio
from datetime import datetime

# from make_celery import celery_app

@shared_task(name='my_task')
def my_task():
    print('my_task')
    return 'my_task'

@shared_task(ignore_result=False)
def test():
    from flask import current_app
    redis = current_app.extensions['redis']
    print(redis.keys())
    # celery_app.add_periodic_task(10, my_task.s())
    print('test----')
    return 'test'

@shared_task(ignore_result=False)
def block():
    time.sleep(5)
    return 'hello world'

@shared_task(bind=True, ignore_result=False)
def process(self: Task, total: int) -> object:
    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": total})
        time.sleep(1)
    return {"current": total, "total": total}


@shared_task(name='weixin')
def weixin():
    from crawler.article import main
    redis_cli = current_app.extensions['redis']
    print('start weixin task')
    return asyncio.run(main(db, redis_cli))

@shared_task(bind=True)
def manage_periodic_task(self):
    print(self)
    print(dir(self))
    return '1'


@shared_task(ignore_result=False)
def add(a: int, b: int) -> int:
    username = random.choice(['a', 'b', 'c', 'd'])
    userpassword = str(random.randint(1, 100))
    print('add: ', datetime.now())
    # book = Book(
    #     username=username,
    #     userpassword=userpassword
    # )
    # db.session.add(book)
    # db.session.commit()
    return '{}: {}'.format(username, userpassword)




