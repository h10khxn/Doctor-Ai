from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/about")
def about():
    return render_template("about.html")


@pages_bp.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")
