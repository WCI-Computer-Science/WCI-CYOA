from flask import Blueprint, render_template, current_app

bp = Blueprint("index", __name__, url_prefix="/")

@bp.route("/", methods=("GET",))
def home():
    return render_template("index.html")

@bp.route("/param/<param>", methods=("GET",))
def param(param):
    return render_template("urlparam.html", param=param)