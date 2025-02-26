from flask import (Blueprint, render_template, request, redirect, url_for)
from webapp.get_data import (get_all_specializations, get_date_set,
                             get_time_set, get_list_dict_mentors,
                             get_user_data, parcel_date_str, parcel_time_str,
                             search_mentors)
from webapp.update_data import create_event
from webapp import settings_conf

mentors_blueprint = Blueprint('mentors', __name__, url_prefix='/mentors')
homepage_title = "MentorMatch Calendar"


@mentors_blueprint.route("/", methods=["POST"])
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


@mentors_blueprint.route("/mentors_search")
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


@mentors_blueprint.route("/mentors_search/book_time", methods=["POST"])
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


@mentors_blueprint.route("/book_time/find_timslots")
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
            return redirect(url_for("calendar.my_calendar",
                                    successful_create=True,
                                    telegram=telegram,
                                    telegram_id=telegram_id))
        else:
            return redirect(url_for("calendar.my_calendar", error_create=True,
                                    telegram=telegram,
                                    telegram_id=telegram_id))
        
    return render_template("post_redirect.html",
                           chose_date_val=chose_date_val,
                           chose_time=chose_time_ids,
                           date=date, gmt=gmt, gmt_sign=gmt_sign,
                           mentor_telegram_id=mentor_telegram_id,
                           telegram=telegram, telegram_id=telegram_id,
                           time=time)
