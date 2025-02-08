from datetime import datetime
import logging
from webapp import settings_conf
from flask import Flask, render_template, request, redirect, url_for
from .get_data import (get_user_data, get_all_specializations, get_date_set,
                       generate_time_list, get_time_set,
                       search_mentors, get_list_dict_mentors, get_my_calendar,
                       get_my_calendar_gmt,
                       parcel_date_str, parcel_time_str)
from .update_data import (change_data, check_username_and_update, save_profile,
                          save_timeslots, cancel_db_event, delete_db_timeslot,
                          approve_db_event, create_event)




# Настройка логирования
logging.basicConfig(
    filename='app.log',  # Файл для логов
    level=logging.INFO,   # Уровень логирования (можно DEBUG, WARNING, ERROR)
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def create_app():

    app = Flask(__name__)
    homepage_title = "MentorMatch Calendar"

    @app.route("/")
    def homepage():
        telegram_id = int(request.args.get("telegram_id"))
        telegram = request.args.get("telegram")
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
        return render_template("homepage.html",
                               admin=settings_conf.ADMIN_ROLE_ID,
                               mentor_role_id=settings_conf.MENTOR_ROLE_ID,
                               mistake_creation=mistake_creation, name=name,
                               page_title=homepage_title, role_id=role_id,
                               successful_creation=successful_creation,
                               telegram=telegram, telegram_id=telegram_id)

    @app.route("/my_profile")
    def my_profile():
        title = "My profile"
        telegram = request.args.get("telegram")
        telegram_id = int(request.args.get("telegram_id"))
        check_username_and_update(telegram, telegram_id)
        editing = request.args.get("editing", default=False, type=bool)
        user_data = get_user_data(telegram_id)
        role_id = set()
        if not user_data:
            return redirect(url_for("homepage", telegram=telegram,
                                    telegram_id=telegram_id))
        name = user_data.get("name")
        role_id = user_data.get("role_id")
        return render_template("profile.html", editing=editing,
                               homepage=homepage_title,
                               mentor_role_id=settings_conf.MENTOR_ROLE_ID,
                               name=name, page_title=title, role_id=role_id,
                               telegram=telegram, telegram_id=telegram_id,
                               user_data=user_data)

    @app.route("/edit_info", methods=["POST"])
    def edit_info():
        telegram = request.form.get("telegram")
        telegram_id = int(request.form.get("telegram_id"))
        action = request.form.get("action")
        if action == "edit":
            return redirect(url_for("my_profile", editing=True,
                                    telegram=telegram,
                                    telegram_id=telegram_id))
        elif action == "cancel":
            return redirect(url_for("my_profile", telegram=telegram,
                                    telegram_id=telegram_id))
        elif action == "submit":
            request_form = request.form
            change_data(request_form)
        return redirect(url_for("my_profile", telegram=telegram,
                                telegram_id=telegram_id))

    @app.route("/my_calendar")
    def my_calendar():
        title = ("My calendar:")
        today = datetime.now()
        filter_date = request.args.get("filter_date")
        if filter_date:
            filter_date = datetime.strptime(filter_date, "%Y-%m-%d")
            filter = request.args.get("action")
        else:
            filter_date = today
            filter = "filter_later"
        telegram = request.args.get("telegram")
        telegram_id = int(request.args.get("telegram_id"))
        gmt = request.args.get("gmt")
        gmt_sign = request.args.get("gmt_sign")
        successful_cancel = request.args.get("successful_cancel",
                                             default=False, type=bool)
        error_delete = request.args.get("error_delete", default=False,
                                        type=bool)
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
        events_gmt = get_my_calendar_gmt(events, gmt, gmt_sign, filter,
                                         filter_date)
        if filter == "reset":
            filter_date = None
        return render_template("my_calendar.html", events_gmt=events_gmt,
                               error_cancel=error_cancel,
                               error_create=error_create,
                               error_delete=error_delete,
                               filter_date=filter_date, gmt=gmt,
                               gmt_sign=gmt_sign, homepage=homepage_title,
                               mentor_role_id=settings_conf.MENTOR_ROLE_ID,
                               name=name, page_title=title, role_id=role_id,
                               successful_cancel=successful_cancel,
                               successful_create=successful_create,
                               telegram=telegram, telegram_id=telegram_id,
                               today=today, user_id=user_id)

    @app.route("/my_profile/create_time_slots")
    def create_time_slots():
        title = "Time slots"
        telegram = request.args.get("telegram")
        telegram_id = int(request.args.get("telegram_id"))
        successful_save = request.args.get("successful_save", default=False,
                                           type=bool)
        mistake_save = request.args.get("mistake_save", default=False,
                                        type=bool)
        user_data = get_user_data(telegram_id)
        if not user_data:
            return redirect(url_for("homepage", telegram=telegram,
                                    telegram_id=telegram_id))
        name = user_data.get("name")
        role_id = user_data.get("role_id")
        time_list = generate_time_list(settings_conf.START_TIME_SLOTS,
                                       settings_conf.END_TIME_SLOTS,
                                       settings_conf.INTERVAL_MINUTES)
        return render_template("timeslots.html", homepage=homepage_title,
                               name=name,
                               mentor_role_id=settings_conf.MENTOR_ROLE_ID,
                               mistake_save=mistake_save, page_title=title,
                               role_id=role_id,
                               successful_save=successful_save,
                               telegram=telegram, telegram_id=telegram_id,
                               time_list=time_list)

    @app.route("/my_profile/update_time_slots", methods=["POST"])
    def update_time_slots():
        telegram = request.form.get("telegram")
        telegram_id = int(request.form.get("telegram_id"))
        action = request.form.get("action")
        if action == "create":
            request_form = request.form
            user_db = get_user_data(telegram_id)
            if not user_db:
                return redirect(url_for("my_profile", telegram=telegram,
                                        telegram_id=telegram_id))
            save = save_timeslots(request_form, user_db["gmt"],
                                  user_db["gmt_sign"], telegram_id)
            if not save:
                return redirect(
                    url_for("create_time_slots", mistake_save=True,
                            telegram=telegram, telegram_id=telegram_id))
            else:
                return redirect(
                    url_for("create_time_slots", successful_save=True,
                            telegram=telegram, telegram_id=telegram_id))
        return redirect(url_for("my_profile", telegram=telegram,
                                telegram_id=telegram_id))

    @app.route("/mentors", methods=["POST"])
    def mentors():
        title = "Mentors"
        telegram = request.form.get("telegram")
        telegram_id = int(request.form.get("telegram_id"))
        search_result_str = request.form.get("search_result")
        search_query_str = request.form.get("search_query")
        search_result = get_list_dict_mentors(search_result_str)
        if search_query_str and not search_result:
            search_result = "empty"
        user_data = get_user_data(telegram_id)
        role_id = set()
        blocked = False
        name = None
        if user_data:
            role_id = user_data.get("role_id")
            blocked = user_data.get("mentors_blocked")
            name = user_data.get("name")
        return render_template("mentors.html", blocked=blocked,
                               homepage=homepage_title,
                               mentor_role_id=settings_conf.MENTOR_ROLE_ID,
                               name=name, page_title=title, role_id=role_id,
                               search_result=search_result,
                               search_query=search_query_str,
                               telegram=telegram, telegram_id=telegram_id)

    @app.route("/mentors/mentors_search")
    def mentors_search():
        telegram = request.args.get("telegram")
        telegram_id = int(request.args.get("telegram_id"))
        action = request.args.get("action")
        if action == "registration":
            return redirect(url_for("mentors_registration", telegram=telegram,
                                    telegram_id=telegram_id))
        elif action == "request_to_admin":
            pass
            return redirect(url_for("homepage", telegram=telegram,
                                    telegram_id=telegram_id))
        create_event = request.args.get("create_event")
        if create_event:
            return render_template("post_redirect.html",
                                   mentor_telegram_id=create_event,
                                   telegram=telegram, telegram_id=telegram_id)
        search_query = request.args.get("search-mentors")
        if not search_query:
            return render_template("post_redirect.html",
                                   search_result=" ",
                                   search_query=" ",
                                   telegram=telegram,
                                   telegram_id=telegram_id
                                   )
        if action == "search":
            search_result = search_mentors(search_query, telegram_id,
                                           settings_conf.MENTOR_ROLE_ID)
            return render_template("post_redirect.html",
                                   search_result=search_result,
                                   search_query=search_query,
                                   telegram=telegram, telegram_id=telegram_id)
        return redirect(url_for("homepage", telegram=telegram,
                                telegram_id=telegram_id))

    @app.route("/mentors/mentors_registration")
    def mentors_registration():
        title = "Mentors registration form"
        telegram = request.args.get("telegram")
        telegram_id = int(request.args.get("telegram_id"))
        all_specializations = get_all_specializations()
        return render_template("mentors_registration.html",
                               all_specializations=all_specializations,
                               homepage=homepage_title, page_title=title,
                               role_id=settings_conf.MENTOR_ROLE_ID,
                               telegram=telegram, telegram_id=telegram_id)

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
        telegram_id = int(request.form.get("telegram_id"))
        telegram = request.form.get("telegram")
        approve = False
        cancel_event_id = request.form.get("event_id")
        cancel_event_id_approve = request.form.get("event_id_approve")
        if cancel_event_id_approve:
            cancel_event_id = cancel_event_id_approve
            approve = True
        result_delete = cancel_db_event(cancel_event_id,
                                        settings_conf.FREE_CANCEL_HOURS,
                                        telegram_id, approve)
        if result_delete:
            return redirect(url_for("my_calendar", successful_cancel=True,
                                    telegram=telegram, telegram_id=telegram_id))
        return redirect(url_for("my_calendar", error_cancel=True,
                                telegram=telegram, telegram_id=telegram_id))

    @app.route("/approve_event", methods=["POST"])
    def approve_event():
        telegram_id = int(request.form.get("telegram_id"))
        telegram = request.form.get("telegram")
        approve_event_id = request.form.get("event_id")
        result_approve = approve_db_event(approve_event_id)
        if result_approve:
            return redirect(url_for("my_calendar", successful_approve=True,
                                    telegram=telegram, telegram_id=telegram_id))
        return redirect(url_for("my_calendar", error_approve=True,
                                telegram=telegram, telegram_id=telegram_id))

    @app.route("/delete_timeslot", methods=["POST"])
    def delete_timeslot():
        telegram_id = int(request.form.get("telegram_id"))
        telegram = request.form.get("telegram")
        delete_timeslot_id = request.form.get("slot_id")
        result_delete, error = delete_db_timeslot(delete_timeslot_id)
        logging.error("Error in __init__ - delete_timeslot() with mistake"
                     f" - {error} ")
        if result_delete:
            return redirect(url_for("my_calendar", successful_delete=True,
                                    telegram=telegram, telegram_id=telegram_id)
                            )
        return redirect(url_for("my_calendar", error_delete=True,
                                telegram=telegram, telegram_id=telegram_id))

    @app.route("/mentors/mentors_search/book_time", methods=["POST"])
    def book_time():
        title = "Mentor booking"
        telegram = request.form.get("telegram")
        telegram_id = int(request.form.get("telegram_id"))
        gmt = request.form.get("gmt")
        gmt_sign = request.form.get("gmt_sign")
        user_data = get_user_data(telegram_id)
        if user_data:
            role_id = user_data.get("role_id")
            name = user_data.get("name")
        else:
            role_id = set()
            name = None
        mentor_telegram_id = request.form.get("mentor_telegram_id")
        date = request.form.get("date")
        chose_date_val = request.form.get("chose_date")
        if date and not chose_date_val:
            date = parcel_date_str(date)
        time = request.form.get("time")
        chose_time = request.form.get("chose_time")
        if time and not chose_time:
            time = parcel_time_str(time)
        mentor_data = get_user_data(mentor_telegram_id)
        return render_template("booking_mentor.html",
                               chose_date_val=chose_date_val, chose_time=chose_time,
                               date=date, gmt=gmt, gmt_sign=gmt_sign,
                               homepage=homepage_title,
                               mentor_data=mentor_data,
                               mentor_role_id=settings_conf.MENTOR_ROLE_ID,
                               name=name, page_title=title, role_id=role_id,
                               telegram=telegram, telegram_id=telegram_id,
                               time=time)

    @app.route("/mentors/book_time/find_timslots")
    def find_timslots():
        telegram = request.args.get("telegram")
        telegram_id = int(request.args.get("telegram_id"))
        chose = request.args.get("chose")
        gmt = request.args.get("gmt")
        gmt_sign = request.args.get("gmt_sign")
        mentor_telegram_id = request.args.get("mentor_telegram_id")
        chose_date_val = request.args.get("chose_date") or ""
        chose_time_ids = request.args.getlist("chose_time") or ""
        create_booking = request.args.get("create_booking") or ""
        description = request.args.get("description")
        date = ""
        time = ""
        if chose == "chose_gmt" or chose == "edit_date":
            date = get_date_set(mentor_telegram_id, gmt, gmt_sign) or ""
            chose_date_val = ""
        elif chose == "chose_date" or chose == "edit_time":
            time = (get_time_set(mentor_telegram_id, gmt, gmt_sign,
                                 chose_date_val)
                    or "")
            chose_time_ids = ""
        elif create_booking:
            result_creation = create_event(telegram_id, telegram, description,
                                           chose_time_ids)
            if result_creation:
                return redirect(url_for("my_calendar", successful_create=True,
                                        telegram=telegram,
                                        telegram_id=telegram_id))
            else:
                return redirect(url_for("my_calendar", error_create=True,
                                        telegram=telegram,
                                        telegram_id=telegram_id))
            
        return render_template("post_redirect.html",
                               chose_date_val=chose_date_val,
                               chose_time=chose_time_ids,
                               date=date, gmt=gmt, gmt_sign=gmt_sign,
                               mentor_telegram_id=mentor_telegram_id,
                               telegram=telegram, telegram_id=telegram_id,
                               time=time)

    @app.route("/admin")
    def admin():
        title = "Admin"
        return render_template("admin.html", page_title=title)

    @app.route("/request_to_admin")
    def request_to_admin():
        title = "Request to admin"
        return render_template("request_to_admin.html", page_title=title)

    return app

app = create_app()
