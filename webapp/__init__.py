from datetime import datetime
import logging
from webapp import settings_conf
from flask import Flask, render_template, request, redirect, url_for
from .get_data import (get_user_data, get_all_specializations, get_date_set,
                       generate_time_list, get_time_set,
                       search_mentors, get_list_dict_mentors, get_my_calendar,
                       get_my_calendar_gmt,
                       parcel_date_str, parcel_time_str)
from .update_data import (action_with_event_timeslot, change_data,
                          check_username_and_update, save_profile,
                          save_timeslots, create_event)


def create_app():

    app = Flask(__name__)
    homepage_title = "MentorMatch Calendar"

    @app.route("/")
    def homepage():
        telegram_id = int(request.args.get("telegram_id"))
        telegram = request.args.get("telegram")
        successful_creation = request.args.get("successful_creation") or ""
        mistake_creation = request.args.get("mistake_creation") or ""
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
        logger = logging.getLogger("gunicorn.error")
        logger.debug("starting my profile")
        telegram = request.args.get("telegram")
        telegram_id = int(request.args.get("telegram_id"))
        logger.debug("Telegram and telegram_id collected")
        logger.error("123")
        check_username_and_update(telegram, telegram_id)
        editing = request.args.get("editing", default=False, type=bool)
        user_data = get_user_data(telegram_id)
        logger.debug("User data collected")
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
        action_event = ""
        type_modal = request.args.get("type_modal")
        title = ("My calendar:")
        today = datetime.now()
        filter_date = request.args.get("filter_date")
        filter = request.args.get("action") or "filter_later"
        if filter_date:
            filter_date = datetime.strptime(filter_date, "%Y-%m-%d")
        else:
            filter_date = today
        telegram = request.args.get("telegram")
        telegram_id = int(request.args.get("telegram_id"))

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
            user_id, name = None, None
            gmt = request.args.get("gmt")
            gmt_sign = request.args.get("gmt_sign")
            role_id = set()

        if filter == "reset":
            filter_date = None

        event_id = request.args.get("event_id")
        timeslot_id = request.args.get("timeslot_id")
        (successful_approve, error_approve, successful_cancel, error_cancel,
         successful_delete, error_delete, action_event
         ) = action_with_event_timeslot(
            type_modal, telegram_id, event_id, timeslot_id)

        events = get_my_calendar(telegram_id)
        events_gmt = get_my_calendar_gmt(events, gmt, gmt_sign, filter,
                                         filter_date)
        return render_template("my_calendar.html", action_event=action_event,
                               events_gmt=events_gmt,
                               error_approve=error_approve,
                               error_cancel=error_cancel,
                               error_create=error_create,
                               error_delete=error_delete,
                               filter_date=filter_date, gmt=gmt,
                               gmt_sign=gmt_sign, homepage=homepage_title,
                               mentor_role_id=settings_conf.MENTOR_ROLE_ID,
                               name=name, page_title=title, role_id=role_id,
                               successful_approve=successful_approve,
                               successful_cancel=successful_cancel,
                               successful_create=successful_create,
                               successful_delete=successful_delete,
                               telegram=telegram, telegram_id=telegram_id,
                               today=today, user_id=user_id)

    @app.route("/my_profile/create_time_slots")
    def create_time_slots():
        title = "Time slots"
        telegram = request.args.get("telegram")
        telegram_id = int(request.args.get("telegram_id"))
        successful_save = request.args.get("successful_save") or ""
        mistake_save = request.args.get("mistake_save") or ""
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
        create_event = request.args.get("create_event")
        search_query = request.args.get("search-mentors")
        if action == "registration":
            title = "Mentors registration form"
            all_specializations = get_all_specializations()
            return render_template("mentors_registration.html",
                                   all_specializations=all_specializations,
                                   homepage=homepage_title, page_title=title,
                                   role_id=settings_conf.MENTOR_ROLE_ID,
                                   telegram=telegram, telegram_id=telegram_id)
        elif action == "request_to_admin":
            pass
            return redirect(url_for("homepage", telegram=telegram,
                                    telegram_id=telegram_id))
        elif create_event:
            return render_template("post_redirect.html",
                                   mentor_telegram_id=create_event,
                                   telegram=telegram, telegram_id=telegram_id)
        elif not search_query:
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

    @app.route("/mentors/mentors_registration", methods=["POST"])
    def create_profile():
        telegram_id = int(request.form.get("telegram_id"))
        telegram = request.form.get("telegram")
        mentor_role_id = int(request.form.get("role_id"))
        save_profile(request.form)
        user_db = get_user_data(telegram_id)
        if user_db:
            role_id = user_db.get("role_id")
            if mentor_role_id in role_id:
                print("----**888888*8*")
                return redirect(url_for("homepage", mistake_creation="",
                                        successful_creation=True,
                                        telegram=telegram,
                                        telegram_id=telegram_id))
        return redirect(url_for("homepage", mistake_creation=True,
                                successful_creation="", telegram=telegram,
                                telegram_id=telegram_id))

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
                               chose_date_val=chose_date_val,
                               chose_time=chose_time, date=date, gmt=gmt,
                               gmt_sign=gmt_sign, homepage=homepage_title,
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
