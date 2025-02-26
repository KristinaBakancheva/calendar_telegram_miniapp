from datetime import datetime
from flask import (Blueprint, render_template, request)
from webapp.get_data import (get_my_calendar, get_my_calendar_gmt,
                             get_user_data)
from webapp.update_data import action_with_event_timeslot
from webapp import settings_conf

calendar_blueprint = Blueprint('calendar', __name__, url_prefix='/my_calendar')
homepage_title = "MentorMatch Calendar"


@calendar_blueprint.route("/")
def my_calendar():
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
        gmt = request.args.get("gmt") or "00:00"
        gmt_sign = request.args.get("gmt_sign") or "+"
        role_id = set()
    if filter == "reset":
        filter_date = None
    event_id = request.args.get("event_id")
    timeslot_id = request.args.get("timeslot_id")
    # result action with event or timeslot
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

    