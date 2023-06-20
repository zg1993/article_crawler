# -*- coding: utf-8 -*-
from celery import shared_task, Task
import time
from .model import Article, Book
from .db import db

import random



@shared_task(ignore_result=False)
def test():
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


@shared_task
def weixin():
    pass

@shared_task(ignore_result=False)
def add(a: int, b: int) -> int:
    username = random.choice(['a', 'b', 'c', 'd'])
    userpassword = str(random.randint(1, 100))
    book = Book(
        username=username,
        userpassword=userpassword
    )
    db.session.add(book)
    db.session.commit()
    return '{}: {}'.format(username, userpassword)




