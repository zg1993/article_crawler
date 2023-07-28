from .db import db
from sqlalchemy.orm.attributes import InstrumentedAttribute
from flask import current_app
from sqlalchemy import func


class Book(db.Model):  # 让Book 继承基类的模型
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    userpassword = db.Column(db.String(20), nullable=False)


class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    official_accounts = db.Column(db.JSON, nullable=False)
    search_keys = db.Column(db.JSON, nullable=False)
    delta = db.Column(db.Integer, nullable=False, default=0)
    period = db.Column(db.String(20), nullable=False, default='23:50')
    status = db.Column(db.SMALLINT, nullable=False, default=0)
    source = db.Column(db.String(50), nullable=False, default='微信公众号')
    last_execute_time = db.Column(db.DateTime, nullable=True)
    execute_status = db.Column(db.SmallInteger,default=1)
    start_time = db.Column(db.String(20), default='')
    end_time = db.Column(db.String(20), default='')
    # delete_time=db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return 'task {} {}'.format(self.id, self.name)

    def to_json(self):
        res = {}
        for key in dir(self):
            if not key.startswith('_') and isinstance(getattr(self.__class__, key), InstrumentedAttribute):
                res[key] = getattr(self, key)
            if 'last_execute_time' == key and getattr(self, key):
                res['last_execute_time'] = getattr(self, key).strftime('%Y-%m-%d %H:%M:%S')
        return res
    

class Article(db.Model):
    __tablename__ = 'article'
    aid = db.Column(db.String(20), primary_key=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    link = db.Column(db.Text, nullable=False)
    # update_time = db.Column(db.TIMESTAMP(True),
    #                         nullable=False,
    #                         onupdate=db.text('CURRENT_TIMESTAMP'))
    update_time = db.Column(db.Integer, nullable=False)
    cover = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text(65536), nullable=True)
    topic = db.Column(db.Integer, db.ForeignKey('task.id', ondelete='SET NULL'), default=1) # task table id
    extracted_from = db.Column(db.String(50), default='')

    def __repr__(self):
        return 'Article {} {} {}'.format(self.aid, self.title,
                                         self.update_time)
    
    def keys(self):
        return ['aid', 'title', 'link', 'update_time', 'cover']

    def __getitem__(self, item):
        return getattr(self, item)

    def to_json(self):
        res = {}
        for key in dir(self):
            if not key.startswith('_') and isinstance(getattr(self.__class__, key), InstrumentedAttribute):
                res[key] = getattr(self, key)
        res['update_time'] = res['update_time'] * 1000
        return res

    #id INT NOT NULL AUTO_INCREMENT,
    #   title VARCHAR(200) NOT NULL,
    #   update_time INT NOT NULL,
    #   tsp TIMESTAMP NOT NULL,
    #   content MEDIUMTEXT,
    #   js json NOT NULL,
    #   PRIMARY KEY (`id`)

class Test(db.Model):
    __name__ = 'test'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    update_time = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200),unique=True, nullable=False)
    tsp = db.Column(db.TIMESTAMP, nullable=False)
    content = db.Column(db.Text(65536), nullable=True)
    js = db.Column(db.JSON, nullable=False)
    delete_time = db.Column(db.DateTime, nullable=True)


    def to_json(self):
        res = {}
        for key in dir(self):
            if not key.startswith('_') and isinstance(getattr(self.__class__, key), InstrumentedAttribute):
                res[key] = getattr(self, key)
            if 'delete_time' == key and getattr(self, key):
                res['delete_time'] = getattr(self, key).strftime('%Y-%m-%d %H:%M:%S')
        # res['update_time'] = res['update_time'] * 1000
        return res