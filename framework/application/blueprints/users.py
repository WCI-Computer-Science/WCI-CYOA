from flask import Blueprint, render_template, flash, current_app, request, redirect, session

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.route("/", methods=("GET",))
def profile():
    return render_template("users.html", username="placeholder for now", clicks=0)
