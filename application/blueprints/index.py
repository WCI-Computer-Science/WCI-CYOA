from flask import Blueprint, render_template, current_app

bp = Blueprint("index", __name__, url_prefix="/")

def get_start_page():
    return 0

@bp.route("/")
def home():
    return render_template("index.html")

@bp.route("/game/<pageid>")
def param(pageid):
    if pageid.lower=="start":
        pageid = get_start_page()
    return render_template("gamepage.html", param=param)