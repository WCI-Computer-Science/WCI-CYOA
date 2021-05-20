from flask import Blueprint, render_template, flash, current_app, request, redirect, session
from application.models.database import get_db
import os, hashlib

bp = Blueprint("users", __name__, url_prefix="/users")

def hash_pass(password, salt=None):
    salt = os.urandom(32) if salt == None else salt
    hashed_pass = hashlib.pbkdf2_hmac(
    'sha256',
    password.encode('utf-8'),
    salt,
    100000)
    return hashed_pass, salt


@bp.route("/", methods=("GET",))
def profile():
    if "email" not in session:
        return redirect("/users/login")

    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT username, clicks FROM users WHERE email=%s LIMIT 1", (session["email"]))
        res = cur.fetchone()
    return render_template("users.html", username=res[0], clicks=res[1])

@bp.route("/signup", methods=("GET",))
def signup():
    if "email" in session:
        return redirect("/users")
    return render_template("login.html", title="Sign up", action="confirmsignup", display="none")

@bp.route("/confirmsignup", methods=("POST",))
def confirmsignup():
    if "email" in session:
        return redirect("/users")
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE username=%s LIMIT 1", (str(request.form["username"])))
        res = cur.fetchone()
        if res:
            flash("Account already exists")
            return redirect("/users/signup")
        cur.execute(
            "INSERT INTO users (username, password_hash, password_salt) VALUES (%s, %s, %s)",
            (str(request.form["username"]),) + hash_pass(str(request.form["password"]))
        )
    
    db.commit()
    return redirect("/users")

@bp.route("/login", methods=("GET",))
def login():
    if "email" in session:
        return redirect("/users")
    return render_template("login.html", title="Login", action="confirmlogin")

@bp.route("/logout", methods=("GET",))
def logout():
    session.clear()
    return redirect("/")

@bp.route("/confirmlogin", methods=("POST",))
def confirmlogin():
    if "email" in session:
        return redirect("/users")
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (str(request.form["email"]), str(request.form["password"]))
        )
        res = cur.fetchone()
        if not res:
            flash("Either account doesn't exist or incorrect password")
            return redirect("/users/login")
    
    session["email"] = request.form["email"]
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
            (str(session["email"]))
        )
    db.commit()
    return "Success"
