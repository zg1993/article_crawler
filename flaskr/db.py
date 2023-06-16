# -*- coding: utf-8 -*-

import click
from flask import current_app, g

from flask_sqlalchemy import SQLAlchemy

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


@click.command('init-db')
def init_db_command():
    print('init_db-----')
    init_db()
    click.echo('Initialized the database.')


def init(app):
    # app.teardown_appcontext(close_db)
    db.init_app(app)
    app.cli.add_command(init_db_command)
    
    


 