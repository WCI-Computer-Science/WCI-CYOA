from flask import Blueprint, render_template, current_app, redirect, abort, session, request
from application.models.database import get_db
from random import randint, shuffle

bp = Blueprint("index", __name__, url_prefix="/")

def get_start_page():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT pagehash FROM protected_pages WHERE pagenumber=1 LIMIT 1"
        )
        res = cur.fetchone()
        if res == None:
            return 0
    return res[0]

def get_team(key):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT team FROM users WHERE key=%s LIMIT 1",
            (str(key),)
        )
        res = cur.fetchone()
        return int(res[0]) if res!=None else 3

def make_game(length=None):
    length = 9000 if length==None else int(length)
    goallength = randint(int(length/40), int(length/18))
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "DELETE FROM protected_pages"
        )
        pages = list(range(length))
        orderedpages = list(range(length))
        shuffle(pages)
        for i in range(1, goallength+1):
            gamepagenumber = pages.pop()
            cur.execute(
                "INSERT INTO protected_pages (pagenumber, pagehash, final, gamepagenumber) VALUES (%s, %s, %s, %s)",
                (i, hash(hash(str(gamepagenumber))), i==goallength, gamepagenumber)
            )
    db.commit()

@bp.route("/")
def home():
    return render_template("index.html")

@bp.route("/game/<pageid>")
def game(pageid):
    if pageid.lower()=="start":
        pageid = get_start_page()
        if pageid == 0:
            abort(403)
        return redirect("/game/" + pageid)
    return render_template("gamepage.html", name=pageid)

@bp.route("/gamesetup/makegame")
def generate_game():
    team = get_team(session["key"])
    if team!=0:
        abort(401)
    make_game(length=request.args.get("length", None))
    return "Success!"
    