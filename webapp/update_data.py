from datetime import datetime, timedelta
from db import db_session
from models import (UserSpecialization, User, UserRole, TimeSlots, Status,
                    Events)
from .get_data import (get_user_by_telegram, get_list_specialization_id,
                       get_client_by_telegram, get_status_id)
from webapp import settings_conf


def check_username_and_update(telegram_username, telegram_id):
    user_db = get_user_by_telegram(telegram_id)
    if user_db and user_db.telegram != "@"+telegram_username:
        user_db.telegram = "@"+telegram_username
        db_session.commit()


def change_data(request_form):
    """
    The function updates information in users and find outdated and new
    specializations for user
    """
    telegram_id = request_form.get("telegram_id")
    user_db = get_user_by_telegram(telegram_id)
    if user_db:
        user_db.telegram = request_form.get("telegram")
        user_db.name = request_form.get("name")
        user_db.description = request_form.get("description")
        user_db.gmt = request_form.get("gmt")
        user_db.gmt_sign = request_form.get("gmt_sign")
    if request_form.get("phone"):
        user_db.phone = request_form.get("phone")
    new_specializations = request_form.getlist("specialization")
    db_specializations_id = get_list_specialization_id(user_db)
    del_list = list()
    add_list = list()
    if user_db.id is not None:
        if request_form.get("role_id"):
            new_role = UserRole(user_id=user_db.id,
                                role_id=request_form.get("role_id")
                                )
            db_session.add(new_role)
        del_list = check_outdated_specialization(
            user_db.id, new_specializations, db_specializations_id)
        add_list = check_new_specialization(
            user_db.id, new_specializations)
        for el in del_list:
            db_session.delete(el)
        for el in add_list:
            db_session.add(el)
        db_session.commit()


def create_user_special(user_id, user_specialization_id):
    """
    The function creates new pair user_id and specialization_id
    for class UserSpecialization
    """
    user_special = UserSpecialization.query.filter(
        UserSpecialization.user_id == user_id,
        UserSpecialization.specialization_id ==
        user_specialization_id).first()
    return user_special


def check_outdated_specialization(user_id, new_specializations,
                                  db_specializations):
    del_list = list()
    for user_specialization in db_specializations:
        if str(user_specialization) not in new_specializations:
            user_special = create_user_special(
                user_id, user_specialization)
            del_list.append(user_special)
    return del_list


def check_new_specialization(user_id, new_specializations):
    add_list = list()
    for specialization_id in new_specializations:
        specialization_id = int(specialization_id)
        user_special = create_user_special(user_id, specialization_id)
        if not user_special:
            new_user_special = UserSpecialization(
                user_id=user_id, specialization_id=specialization_id)
            add_list.append(new_user_special)
    return add_list


def save_profile(request_form):
    telegram_id = request_form.get("telegram_id")
    user_db = get_user_by_telegram(telegram_id)
    if user_db:
        change_data(request_form)
    else:
        new_user = User(telegram_id=telegram_id,
                        telegram=request_form.get("telegram"),
                        name=request_form.get("name"),
                        phone=request_form.get("phone"),
                        description=request_form.get("description"),
                        gmt=request_form.get("gmt"),
                        gmt_sign=request_form.get("gmt_sign"),
                        mentors_blocked=False)
        db_session.add(new_user)
    db_session.commit()
    new_specializations = request_form.getlist("specialization")
    add_list_special = check_new_specialization(
                                    new_user.id, new_specializations
                                                )
    db_session.add_all(add_list_special)
    if request_form.get("role_id"):
        new_role = UserRole(user_id=new_user.id,
                            role_id=request_form.get("role_id")
                            )
        db_session.add(new_role)
    db_session.commit()


def save_timeslots(request_form, gmt, gmt_sign, telegram_id):
    gmt = gmt.strftime("%H:%M")
    hours, minutes = map(int, gmt.split(":"))
    td = timedelta(hours=hours, minutes=minutes)
    user_db = get_user_by_telegram(telegram_id)
    if not user_db:
        return None
    timeslots = request_form.getlist("time_slot")
    if not timeslots:
        return None
    date = request_form.get("date")
    for timeslot_str in timeslots:
        timeslot = timeslot_str.split(' - ')
        start_date_str = date + " " + timeslot[0]
        end_date_str = date + " " + timeslot[1]
        if gmt_sign == "-":
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M")+td
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M")+td
        else:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M")-td
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M")-td
        new_timeslots = TimeSlots(user_id=user_db.id,
                                  start_date_utc=start_date,
                                  end_date_utc=end_date)
        db_session.add(new_timeslots)
        db_session.commit()
    if new_timeslots.id:
        return True
    return None


def cancel_db_event(cancel_event_id, free_cancel, telegram_id,
                    approve_cancel=False):
    request_mentor_status = Status.query.filter(Status.name.ilike(
        "%request%mentor%")).first()
    request_cancel_status_id = None
    if request_mentor_status:
        request_cancel_status_id = request_mentor_status.id
    today = datetime.now()
    user_db = get_user_by_telegram(telegram_id)
    user_id = None
    if user_db:
        user_id = user_db.id
    client_id = get_client_by_telegram(telegram_id)
    event_slot = db_session.query(Events.id,
                                  Events.slot_id,
                                  Events.status_id,
                                  TimeSlots.id,
                                  TimeSlots.start_date_utc,
                                  TimeSlots.user_id
                                  ).join(
                                    TimeSlots, TimeSlots.id == Events.slot_id
                                        ).filter((Events.id == cancel_event_id)
                                                 ).first()
    if not event_slot:
        return False, "We can't find this event"
    date_slot = event_slot[4]
    difference = date_slot - today
    sec_dif = difference.total_seconds()
    hour_dif = sec_dif/3600
    if (approve_cancel or hour_dif > free_cancel or user_id == event_slot[5] or
       event_slot[2] == request_cancel_status_id):
        event = Events.query.filter(Events.id == cancel_event_id).first()
        if client_id == event.client_id:
            cancel_status = Status.query.filter(Status.name.ilike(
                "%canceled%client")).first()
        else:
            cancel_status = Status.query.filter(Status.name.ilike(
                "%canceled%mentor")).first()
        if not cancel_status:
            return False, "We can't find a 'canceled' by mentor/client status"
        event.status_id = cancel_status.id
    else:
        request_cancel_status = Status.query.filter(
                                            Status.name == "request cancel"
                                                    ).first()
        if request_cancel_status:
            return False, "We can't find a 'request cancel' status"
        event.status_id = request_cancel_status.id
    db_session.commit()
    return True, None


def delete_db_timeslot(delete_timeslot_id):
    all_cancel_status = get_status_id("canceled")
    if not all_cancel_status:
        return False, "We don't have status 'canceled'"
    events = Events.query.filter((Events.slot_id == delete_timeslot_id) &
                                 (Events.status_id.in_(all_cancel_status))
                                 ).first()
    slot = TimeSlots.query.filter(TimeSlots.id == delete_timeslot_id
                                  ).first()
    if not slot:
        return True, None
    elif events:
        slot.active = False
    else:
        db_session.delete(slot)
    db_session.commit()
    return True, None


def approve_db_event(approve_event_id):
    booked_status = Status.query.filter(Status.name == "booked").first()
    request_status = Status.query.filter(Status.name == "request to mentor"
                                         ).first()
    if not booked_status or not request_status:
        return False, "We can't find 'booked' status or 'request to mentor"
    event = Events.query.filter((Events.id == approve_event_id) &
                                (Events.status_id == request_status.id)
                                ).first()
    if not event:
        return False, "We can't find this event"
    event.status_id = booked_status.id
    db_session.commit()
    return True, None


def create_event(telegram_id, telegram, request, list_timeslots_id):
    client_id = get_client_by_telegram(telegram_id, telegram)
    status = Status.query.filter(Status.name == "request to mentor").first()
    if not status:
        return False
    for timeslots_id in list_timeslots_id:
        new_event = Events(slot_id=timeslots_id, client_id=client_id,
                           request=request, status_id=status.id)
        db_session.add(new_event)
        db_session.commit()
    if new_event.id:
        return True
    return False


def action_with_event_timeslot(type_modal, telegram_id, event_id, timeslot_id):
    successful_approve = False
    error_approve = False
    successful_cancel = False
    error_cancel = False
    successful_delete = False
    error_delete = False
    action = ""
    if type_modal == "approve_event":
        result_approve, error = approve_db_event(event_id)
        if result_approve:
            successful_approve = True
            action = "success"
        else:
            error_approve = error
            action = "error"
    elif type_modal == "cancel_event" or type_modal == "approve_cancel_event":
        approve = False
        if type_modal == "approve_cancel_event":
            approve = True
        result_delete, error = cancel_db_event(event_id,
                                               settings_conf.FREE_CANCEL_HOURS,
                                               telegram_id, approve)
        if result_delete:
            successful_cancel = True
            action = "success"
        else:
            error_cancel = error
            action = "error"
    elif type_modal == "delete_time_slot":
        result_delete, error = delete_db_timeslot(timeslot_id)
        if result_delete:
            successful_delete = True
            action = "success"
        else:
            error_delete = error
            action = "error"
    return (successful_approve, error_approve, successful_cancel, error_cancel,
            successful_delete, error_delete, action)
