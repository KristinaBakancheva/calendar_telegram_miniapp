from datetime import datetime
from db import db_session
from flask import Flask, render_template, request, redirect, url_for
from .get_data import (get_user_data, get_all_specializations, get_date_set,
                       generate_time_list, get_user_by_telegram, get_time_set,
                       search_mentors, get_list_dict_mentors, get_my_calendar,
                       get_my_calendar_gmt, get_mentor_timeslots_gmt,
                       parcel_date_str, parcel_time_str)
from .update_data import (change_data, check_username_and_update, save_profile,
                          save_timeslots, cancel_db_event, delete_db_timeslot,
                          approve_db_event, create_event)


def create_app():
    # !!!!!!!!!!заменить @nikbeesti на данные из телеграмм бота from.id и from.username
    mentor_role_id = 1 # id роли ментор
    admin_id = 3 # id роли админ
    telegram_id = 99266796229#90990##266796229 # 284303797 - кристина
    telegram = "nikbeesti"

    start_time = "05:00"
    end_time = "23:00"
    interval_minutes = 30
    free_cancel = 24

    status_active_timeslots = 1

    app = Flask(__name__)
    homepage_title = "MentorMatch Calendar"

    @app.route("/")
    def homepage():
        successful_creation = request.args.get("successful_creation",
                                               "false").lower() == "true"
        mistake_creation = request.args.get("mistake_creation",
                                            "false").lower() == "true"
        user_data = get_user_data(telegram_id)
        role_id = set()
        name = None
        if user_data:
            role_id = user_data.get("role_id")
            name = user_data.get("name")
        return render_template("homepage.html", page_title=homepage_title,
                               successful_creation=successful_creation,
                               mistake_creation=mistake_creation,
                               role_id=role_id, mentor_role_id=mentor_role_id,
                               admin=admin_id, name=name)

    @app.route("/my_profile")
    def my_profile():
        check_username_and_update(telegram, telegram_id)
        editing = request.args.get("editing", default=False, type=bool)
        title = "My profile"
        user_data = get_user_data(telegram_id)
        role_id = set()
        if not user_data:
            return redirect(url_for("homepage"))
        name = user_data.get("name")
        role_id = user_data.get("role_id")
        return render_template("profile.html", page_title=title,
                               homepage=homepage_title, user_data=user_data,
                               editing=editing, name=name, role_id=role_id,
                               mentor_role_id=mentor_role_id)

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

    @app.route("/my_calendar")
    def my_calendar():
        title = ("My calendar:")
        gmt = request.args.get("gmt")
        gmt_sign = request.args.get("gmt_sign")
        successful_cancel = request.args.get("successful_cancel",
                                             default=False, type=bool)
        error_cancel = request.args.get("error_cancel", default=False,
                                        type=bool)
        successful_create = request.args.get("successful_create",
                                             default=False, type=bool)
        error_create = request.args.get("error_create", default=False,
                                        type=bool)
        user_data = get_user_data(telegram_id)
        if user_data:
            user_id = user_data.get("id")
            gmt = user_data.get("gmt")
            gmt_sign = user_data.get("gmt_sign")
            role_id = user_data.get("role_id")
            name = user_data.get("name")
        else:
            role_id = set()
            user_id = None
            name = None
        events = get_my_calendar(telegram_id)
        events_gmt = get_my_calendar_gmt(events, gmt, gmt_sign)
        return render_template("my_calendar.html", page_title=title,
                               homepage=homepage_title, events_gmt=events_gmt,
                               gmt=gmt, gmt_sign=gmt_sign, user_id=user_id,
                               mentor_role_id=mentor_role_id, role_id=role_id,
                               status_active_timeslots=status_active_timeslots,
                               name=name, successful_cancel=successful_cancel,
                               error_cancel=error_cancel,
                               successful_create=successful_create,
                               error_create=error_create)

    @app.route("/my_profile/create_time_slots")
    def create_time_slots():
        successful_save = request.args.get("successful_save", default=False,
                                           type=bool)
        mistake_save = request.args.get("mistake_save", default=False,
                                        type=bool)
        title = "Time slots"
        user_data = get_user_data(telegram_id)
        if not user_data:
            return redirect(url_for("homepage"))
        name = user_data.get("name")
        role_id = user_data.get("role_id")
        time_list = generate_time_list(start_time, end_time, interval_minutes)
        return render_template("timeslots.html", page_title=title,
                               homepage=homepage_title, user_data=user_data,
                               time_list=time_list, name=name,
                               successful_save=successful_save,
                               mistake_save=mistake_save,
                               role_id=role_id, mentor_role_id=mentor_role_id)

    @app.route("/my_profile/update_time_slots", methods=["POST"])
    def update_time_slots():
        action = request.form.get("action")
        if action == "create":
            request_form = request.form
            user_db = get_user_data(telegram_id)
            if not user_db:
                return redirect(url_for("my_profile"))
            save = save_timeslots(request_form, user_db["gmt"], user_db["gmt_sign"], telegram_id,
                                  status_active_timeslots)
            if not save:
                return redirect(
                    url_for("create_time_slots", mistake_save=True))
            else:
                return redirect(
                    url_for("create_time_slots", successful_save=True))
        elif action == "delete":
            pass
        return redirect(url_for("my_profile"))

    @app.route("/mentors")
    def mentors():
        title = "Mentors"
        search_result_list_str = request.args.getlist("search_result")
        search_query = request.args.getlist("search_query")
        search_result = get_list_dict_mentors(search_result_list_str)
        if search_query and not search_result:
            search_result = "empty"
        user_data = get_user_data(telegram_id)
        role_id = set()
        blocked = False
        name = None
        if user_data:
            role_id = user_data.get("role_id")
            blocked = user_data.get("mentors_blocked")
            name = user_data.get("name")
        return render_template("mentors.html", page_title=title,
                               homepage=homepage_title, role_id=role_id,
                               mentor_role_id=mentor_role_id, blocked=blocked,
                               search_result=search_result, name=name,
                               search_query=search_query)

    @app.route("/mentors/mentors_search")
    def mentors_search():
        action = request.args.get("action")
        if action == "registration":
            return redirect(url_for("mentors_registration"))
        elif action == "request_to_admin":
            pass
            return redirect(url_for("homepage"))
        create_event = request.args.get("create_event")
        if create_event:
            return render_template("post_redirect.html",
                                   mentor_telegram_id=create_event)
        search_query = request.args.get("search-mentors")
        if not search_query:
            return redirect(url_for("mentors"))
        if action == "search":
            search_result = search_mentors(
                search_query, telegram_id, mentor_role_id)
            return redirect(url_for("mentors", search_result=search_result,
                                    search_query=search_query))
        return redirect(url_for("homepage"))

    @app.route("/mentors/mentors_registration")
    def mentors_registration():
        all_specializations = get_all_specializations()
        title = "Mentors registration form"
        return render_template("mentors_registration.html", page_title=title,
                               homepage=homepage_title,
                               telegram=telegram,
                               telegram_id=telegram_id,
                               all_specializations=all_specializations,
                               role_id=mentor_role_id
                               )

    @app.route("/mentors/mentors_registration", methods=["POST"])
    def create_profile():
        request_form = request.form
        save_profile(request_form)
        user_db = get_user_data(telegram_id)
        if user_db:
            role_id = user_db.get("role_id")
            if mentor_role_id in role_id:
                return redirect(url_for("homepage", successful_creation=True))
        return redirect(url_for("homepage", mistake_creation=True))

    @app.route("/cancel_event", methods=["POST"])
    def cancel_event():
        approve = False
        cancel_event_id = request.form.get("event_id")
        cancel_event_id_approve = request.form.get("event_id_approve")
        if cancel_event_id_approve:
            cancel_event_id = cancel_event_id_approve
            approve = True
        result_delete = cancel_db_event(cancel_event_id, free_cancel, approve)
        if result_delete:
            return redirect(url_for("my_calendar", successful_cancel=True))
        return redirect(url_for("my_calendar", error_cancel=True))

    @app.route("/approve_event", methods=["POST"])
    def approve_event():
        approve_event_id = request.form.get("event_id")
        result_delete = approve_db_event(approve_event_id)
        if result_delete:
            return redirect(url_for("my_calendar", successful_approve=True))
        return redirect(url_for("my_calendar", error_approve=True))

    @app.route("/delete_timeslot", methods=["POST"])
    def delete_timeslot():
        delete_timeslot_id = request.form.get("slot_id")
        result_delete = delete_db_timeslot(delete_timeslot_id)
        if result_delete:
            return redirect(url_for("my_calendar", successful_delete=True))
        return redirect(url_for("my_calendar", error_delete=True))

    @app.route("/mentors/book_time", methods=["POST"])
    def book_time():
        title = "Mentor booking"
        gmt = request.form.get("gmt")
        gmt_sign = request.form.get("gmt_sign")
        mentor_telegram_id = request.form.get("mentor_telegram_id")
        date = request.form.get("date")
        chose_date = request.form.get("chose_date")
        if date and not chose_date:
            date = parcel_date_str(date)
        time = request.form.get("time")
        chose_time = request.form.get("chose_time")
        if time and not chose_time:
            time = parcel_time_str(time)
        mentor_data = get_user_data(mentor_telegram_id)
        return render_template("booking_mentor.html", page_title=title,
                               homepage=homepage_title, date=date,
                               time=time, mentor_data=mentor_data,
                               gmt=gmt, gmt_sign=gmt_sign,
                               chose_date=chose_date, chose_time=chose_time)

    @app.route("/mentors/book_time/find_timslots")
    def find_timslots():
        chose = request.args.get("chose")
        gmt = request.args.get("gmt")
        gmt_sign = request.args.get("gmt_sign")
        mentor_telegram_id = request.args.get("mentor_telegram_id")
        mentor_id = request.args.get("mentor_id")
        chose_date = request.args.get("choseDate") or ""
        chose_time_id = request.args.getlist("choseTime") or ""
        createBooking = request.args.get("createBooking") or ""
        description = request.args.get("descriptionI")
        date = ""
        time = ""
        if chose == "chose_gmt":
            date = get_date_set(mentor_telegram_id, gmt, gmt_sign)
        elif chose == "chose_date":
            time = get_time_set(mentor_telegram_id, gmt, gmt_sign, chose_date)
        elif createBooking:
            result_creation = create_event(mentor_id, telegram_id, telegram,
                                           description, chose_time_id)
            if result_creation:
                return redirect(url_for("my_calendar", successful_create=True))
            else:
                return redirect(url_for("my_calendar", error_create=True))
        return render_template("post_redirect.html", date=date, time=time,
                               gmt=gmt, gmt_sign=gmt_sign,
                               chose_date=chose_date, chose_time=chose_time_id,
                               mentor_telegram_id=mentor_telegram_id)

    @app.route("/admin")
    def admin():
        title = "Admin"
        return render_template("admin.html", page_title=title)

    @app.route("/request_to_admin")
    def request_to_admin():
        title = "Request to admin"
        return render_template("request_to_admin.html", page_title=title)

    return app
