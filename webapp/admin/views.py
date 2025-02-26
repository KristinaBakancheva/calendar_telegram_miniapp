from flask import (Blueprint, render_template)


admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')
homepage_title = "MentorMatch Calendar"


@admin_blueprint.route("/")
def admin():
    title = "Admin"
    return render_template("admin.html", page_title=title)


@admin_blueprint.route("/request_to_admin")
def request_to_admin():
    title = "Request to admin"
    return render_template("request_to_admin.html", page_title=title)
