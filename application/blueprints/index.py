from flask import Blueprint, render_template, current_app, redirect, abort, session, request
from application.models.database import get_db
from random import randint, shuffle, choice

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
    length = 900 if length==None else int(length)
    goallength = randint(int(length/10), int(length/2))
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "DELETE FROM protected_pages"
        )
        cur.execute(
            "DELETE FROM pages"
        )
        pages = list(range(length))
        shuffle(pages)
        protectedpages = [pages.pop() for i in range(goallength)]
        targetpages = list(pages)
        for i in range(1, goallength+1):
            gamepagenumber = protectedpages[i-1]
            targets = randint(1,3)
            cur.execute(
                "INSERT INTO protected_pages (pagenumber, pagehash, final, gamepagenumber) VALUES (%s, %s, %s, %s)",
                (i, hash(str(hash(str(gamepagenumber)))), i==goallength, gamepagenumber)
            )
            cur.execute(
                "INSERT INTO pages (gamepagenumber, pagehash, target1, target2, target3) VALUES (%s, %s, %s, %s, %s)",
                gamepagenumber,
                hash(str(hash(str(gamepagenumber)))),
                hash(str(hash(str(protectedpages[i])))) if i!=goallength else None,
                hash(str(hash(str(choice(targetpages))))) if targets>1 and i!=goallength else None,
                hash(str(hash(str(choice(targetpages))))) if targets>2 and i!=goallength else None
            )
        for i in pages:
            targets = randint(1,3)
            cur.execute(
                "INSERT INTO pages (gamepagenumber, pagehash, target1, target2, target3) VALUES (%s, %s, %s, %s, %s)",
                (
                    i,
                    hash(str(hash(str(i)))),
                    hash(str(hash(str(choice(targetpages))))),
                    hash(str(hash(str(choice(targetpages))))) if targets>1 else None,
                    hash(str(hash(str(choice(targetpages))))) if targets>2 else None
                )
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
    