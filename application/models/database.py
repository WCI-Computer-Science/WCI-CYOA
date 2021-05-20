import psycopg2
import psycopg2.extras
from flask import current_app, g

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            current_app.config["DATABASE_URL"],
            cursor_factory=psycopg2.extras.DictCursor,
        )
    return g.db

def teardown_db(err=None):
    db = g.pop("db", None)
    if db:
        db.close()

def init_app(app):
    app.teardown_appcontext(teardown_db)
