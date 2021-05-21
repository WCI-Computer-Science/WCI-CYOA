from flask import Blueprint, render_template, current_app

bp = Blueprint("index", __name__, url_prefix="/")

@bp.route("/")
def home():
    return render_template("index.html")

@bp.route("/game/<pageid>")
def param(param):
    return render_template("gamepage.html", param=param)