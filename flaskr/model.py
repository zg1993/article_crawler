from .db import db


class Book(db.Model):  # 让Book 继承基类的模型
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    userpassword = db.Column(db.String(20), nullable=False)


class Article(db.Model):
    __tablename__ = 'article'
    aid = db.Column(db.String(20), primary_key=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    link = db.Column(db.Text, nullable=False)
    update_time = db.Column(db.TIMESTAMP(True),
                            nullable=False,
                            onupdate=db.text('CURRENT_TIMESTAMP'))
    cover = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return 'Article {} {} {}'.format(self.aid, self.title,
                                         self.update_time)
    
    def keys(self):
        return ['aid', 'title', 'link', 'update_time', 'cover']

    def __getitem__(self, item):
        return getattr(self, item)
