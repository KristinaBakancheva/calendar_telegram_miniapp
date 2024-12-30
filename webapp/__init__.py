from flask import Flask, render_template, request, redirect, url_for
from db import db_session
from .get_data import get_user_data, get_user_role
from .check_change_data import change_data, check_username_and_update


def create_app():
    # !!!!!!!!!!заменить @nikbeesti на данные из телеграмм бота from.id и from.username
    telegram_id = 266796229
    telegram_username = "nikbeestiB"

    app = Flask(__name__)
    homepage_title = "MentorMatch Calendar"

    @app.route("/")
    def homepage():
        user_data = get_user_data(telegram_id)
        role_name = ""
        if user_data:
            role_id = user_data["role_id"]
            role_name = get_user_role(role_id)
        return render_template("homepage.html", page_title=homepage_title,
                               role=role_name)

    @app.route("/my_profile")
    def my_profile():
        check_username_and_update(telegram_username, telegram_id)
        editing = request.args.get("editing", default=False, type=bool)
        title = "My profile"
        user_data = get_user_data(telegram_id)
        if not user_data:
            return redirect(url_for("homepage"))
        return render_template("profile.html", title=title,
                               homepage=homepage_title, user_data=user_data,
                               editing=editing)

    @app.route("/edit_info", methods=["POST"])
    def edit_info():
        action = request.form.get("action")
        if action == "edit":
            return redirect(url_for("my_profile", editing=True))
        elif action == "cancel":
            return redirect(url_for("my_profile"))
        elif action == "submit":
            request_form = request.form
            change_data(request_form)
        return redirect(url_for("my_profile"))

    @app.route("/my_profile/time_slots")
    def time_slots():
        title = "Time slots"
        user_data = get_user_data(telegram_id)
        if not user_data:
            return redirect(url_for("homepage"))
        return render_template("timeslots.html", page_title=title,
                               homepage=homepage_title, user_data=user_data)

    @app.route("/my_calendar")
    def my_calendar():
        title = "My calendar"
        return render_template("my_calendar.html", page_title=title)

    @app.route("/mentors")
    def mentors():
        title = "Mentors"
        return render_template("mentors.html", page_title=title,
                               homepage=homepage_title
                               )

    @app.route("/mentors_search", methods=["GET"])
    def mentors_search():
        action = request.form.get("action")
        if action == "search":
            pass
        elif action == "registration":
            return redirect(url_for("mentors_registration"))

    @app.route("/mentors/mentors_registration")
    def mentors_registration():
        title = "Mentors registration form"
        return render_template("mentors_registration.html", page_title=title,
                               homepage=homepage_title
                               )

    @app.route("/admin")
    def admin():
        title = "Admin"
        return render_template("admin.html", page_title=title)

    return app
