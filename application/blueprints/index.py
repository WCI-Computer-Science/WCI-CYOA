from flask import Blueprint, render_template, current_app, redirect, abort
from application.models.database import get_db

bp = Blueprint("index", __name__, url_prefix="/")

def get_start_page():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT pagehash FROM protected_pages WHERE pagenumber=1"
        )
        res = cur.fetchone()
        if res == None:
            return 0
    return res[0]

@bp.route("/")
def home():
    return render_template("index.html")

@bp.route("/game/<pageid>")
def game(pageid):
    if pageid.lower=="start":
        pageid = get_start_page()
        if pageid == 0:
            abort(403)
        return redirect("/game/" + pageid)
    return render_template("gamepage.html", param=pageid)