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
        return (int(res[0]) if res[0]!= None else 4) if res!=None else 3

def page_exists(pagehash):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT pagehash FROM pages WHERE pagehash=%s LIMIT 1",
            (pagehash,)
        )
        return cur.fetchone()!=None

def visitedpage(pagehash, key):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT team FROM users WHERE key=%s LIMIT 1",
            (key,)
        )
        res = cur.fetchone()
        if res==None:
            return
        if res[0]==None:
            return
        team = int(res[0])
        if team == 1:
            cur.execute(
                "UPDATE pages SET team1visited=TRUE WHERE pagehash=%s",
                (pagehash,)
            )
        elif team == 2:
            cur.execute(
                "UPDATE pages SET team2visited=TRUE WHERE pagehash=%s",
                (pagehash,)
            )
    db.commit()
        

def get_page_targets(pagehash):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT target1, target2, target3 FROM pages WHERE pagehash=%s LIMIT 1",
            (pagehash,)
        )
        return cur.fetchone()

def get_win(pagehash):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT final FROM protected_pages WHERE pagehash=%s LIMIT 1",
            (pagehash,)
        )
        res = cur.fetchone()
        return False if res==None else res[0]

def check_win(team):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT pagehash FROM protected_pages"
        )
        pages = cur.fetchall()
        for i in pages:
            if team==1:
                cur.execute(
                    "SELECT team1visited FROM pages WHERE pagehash=%s LIMIT 1",
                    (i[0],)
                )
            elif team==2:
                cur.execute(
                    "SELECT team2visited FROM pages WHERE pagehash=%s LIMIT 1",
                    (i[0],)
                )
            else:
                return False
            res = cur.fetchone()
            if not(res[0]):
                return False
    return True

def make_game(length=None):
    length = 1000 if length==None else int(length)
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
                (
                    gamepagenumber,
                    hash(str(hash(str(gamepagenumber)))),
                    hash(str(hash(str(protectedpages[i])))) if i!=goallength else None,
                    hash(str(hash(str(choice(targetpages))))) if targets>1 and i!=goallength else None,
                    hash(str(hash(str(choice(targetpages))))) if targets>2 and i!=goallength else None
                )
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
        return redirect("/game/" + str(pageid))
    if not(page_exists(pageid)):
        abort(404)
    if "key" in session:
        key = session["key"]
    elif request.args.get("key", None)!=None:
        key = request.args.get("key")
    else: abort(401)
    visitedpage(pageid, key)

    pagetargets = get_page_targets(pageid)
    shuffle(pagetargets)
    win = get_win(pageid)
    if win:
        done = check_win(get_team(key))
    else:
        done = False
    return render_template("gamepage.html", name=pageid, targets=pagetargets, win=win, done=done)

@bp.route("/jointeam/<team>")
def jointeam(team):
    if int(team) not in [1, 2]:
        abort(401)
    if "key" in session:
        key = session["key"]
    else:
        abort(403)
    onteam = get_team(key)
    if onteam==3:
        abort(403)
    if onteam!=4:
        return "You're already on team %s!" % onteam
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE users SET team=%s WHERE key=%s",
            (str(team), key)
        )
    db.commit()
    return "Welcome to team %s!" % team
    

@bp.route("/gamesetup/makegame")
def generate_game():
    team = get_team(session["key"])
    if team!=0:
        abort(401)
    make_game(length=request.args.get("length", None))
    return "Success!"
    