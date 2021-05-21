from flask import Blueprint, render_template, flash, current_app, request, redirect, session
from application.models.database import get_db
import hashlib, os
from secrets import token_urlsafe

bp = Blueprint("users", __name__, url_prefix="/users")

def hash_pass(password, salt=None):
    salt = os.urandom(32) if salt == None else salt
    hashed_pass = hashlib.pbkdf2_hmac(
    'sha256',
    password.encode('utf-8'),
    salt,
    100000)
    return str(hashed_pass), str(salt)

def generate_key():
    return token_urlsafe(32)

@bp.route("/", methods=("GET",))
def profile():
    if "key" not in session:
        return redirect("/users/login")

    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT username FROM users WHERE key=%s LIMIT 1", (str(session["key"]),))
        res = cur.fetchone()
    if res==None:
        session.clear()
        return redirect("/users/login")
    return render_template("users.html", username=res[0])

@bp.route("/signup", methods=("GET",))
def signup():
    if "key" in session:
        return redirect("/users")
    return render_template("login.html", title="Sign up", action="confirmsignup", display="none")

@bp.route("/confirmsignup", methods=("POST",))
def confirmsignup():
    if "key" in session:
        return redirect("/users")
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE username=%s LIMIT 1", (str(request.form["username"])),)
        res = cur.fetchone()
        if res:
            flash("Account already exists")
            return redirect("/users/signup")
        key = str(generate_key())
        password, salt = hash_pass(str(request.form["password"]))
        cur.execute(
            "INSERT INTO users (username, password_hash, password_salt, key) VALUES (%s, %s, %s, %s)",
            (str(request.form["username"]), password, salt, key,)
        )
    
    db.commit()
    session["key"] = key
    return redirect("/users")

@bp.route("/login", methods=("GET",))
def login():
    if "key" in session:
        return redirect("/users")
    return render_template("login.html", title="Login", action="confirmlogin")

@bp.route("/logout", methods=("GET",))
def logout():
    session.clear()
    return redirect("/")

@bp.route("/confirmlogin", methods=("POST",))
def confirmlogin():
    if "key" in session:
        return redirect("/users")
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT password_hash, password_salt, key FROM users WHERE username=%s",
            (str(request.form["username"]),)
        )
        res = cur.fetchone()
        if res == None:
            flash("That account doesn't exist!")
            return redirect("/users/login")
        if hash_pass(request.form["password"], salt=res[1]) != res[0]:
            flash("Incorrect password!")
            return redirect("/users/login")

    session["key"] = key
    return redirect("/users")

# API endpoint
@bp.route("/click", methods=("GET",))
def click():
    if "email" not in session:
        return "Fail"
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE users SET clicks=clicks+1 WHERE email=%s",
            (str(session["email"]),)
        )
    db.commit()
    return "Success"
