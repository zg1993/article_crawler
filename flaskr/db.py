# -*- coding: utf-8 -*-

import click
from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy as BaseSQLAlchemy
from contextlib import contextmanager



class SQLAlchemy(BaseSQLAlchemy):

    @contextmanager
    def auto_commit_db(self, close=True):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            if close:
                self.session.remove()
        

db = SQLAlchemy()



# def get_db():
#     if 'db' not in g:
#         print('current-app',current_app)
#         g.db = SQLAlchemy()
#         # db.create_all()
#     db = g.db
#     return db


# def close_db(e=None):
#     db = g.pop('db', None)
#     if db is not None:
#         db.close()


def init_db():
    # db = get_db()
    from flaskr.model import Book, Article
    db.create_all()

    # book = Book(username='zg', userpassword='123')
    # db.session.add(book)
    # db.session.commit()


@click.command('init-db')
def init_db_command():
    print('init_db-----')
    init_db()
    click.echo('Initialized the database.')


def init(app):
    # app.teardown_appcontext(close_db)
    db.init_app(app)
    app.cli.add_command(init_db_command)
    

    
    


 