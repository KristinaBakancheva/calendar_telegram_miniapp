import ast
from datetime import datetime, timedelta 
from db import db_session
from models import User, Specialization, UserSpecialization, UserRole, Role, TimeSlots, Events, Status, Client
from sqlalchemy import func, desc, or_, and_, union, literal


def get_all_specializations():
    """
    The function returns list of pair name and id of all specializations
    from database
    """

    all_specializations = list()
    for specialization in Specialization.query.all():
        if (
            hasattr(specialization, "name") and specialization.name is not None
            and hasattr(specialization, "id") and specialization.id is not None
           ):
            all_specializations.append(
                (specialization.name, specialization.id))
    sorted_all_specializations = sorted(
        all_specializations, key=lambda x: x[0]
                                        )
    return sorted_all_specializations


def get_user_by_telegram(telegram_id):
    """
    The function uses telegram_id and returns all information from users table.
    """
    data = User.query.filter(User.telegram_id == telegram_id).first()
    if data:
        return data
    else:
        return None  # !!!!! Как правильно обработать такую ошибку?


def get_client_by_telegram(telegram_id, telegram):
    """
    The function uses telegram_id and returns client_id from client table.
    """
    user_id = None
    user = get_user_by_telegram(telegram_id)
    if user:
        user_id = user.id
    data = Client.query.filter(Client.telegram_id == telegram_id).first()
    if not data:
        new_client = Client(telegram_id=telegram_id, telegram=telegram,
                            user_id=user_id)
        db_session.add(new_client)
        db_session.commit()
        return new_client.id
    elif data.user_id != user_id:
        data.user_id = user_id
        db_session.commit()
    return data.id


def get_list_specialization_id(user_data):
    """
    The function returns all specialization_id for user_data.id
    """
    user_specializations_id = list()
    if hasattr(user_data, "id") and user_data.id is not None:
        user_specializations = UserSpecialization.query.filter(
            UserSpecialization.user_id == user_data.id).all()
        if user_specializations:
            user_specializations_id = [
                user_specialization.specialization_id for
                user_specialization in user_specializations]
    return user_specializations_id


def get_user_data(telegram_id):
    """
    The function returns dict with all parametrs from database for telegram_id
    """
    data_user = get_user_by_telegram(telegram_id)
    if not data_user:
        return None
    role_id = set()
    role = UserRole.query.filter(UserRole.user_id == data_user.id).all()
    for el in role:
        role_id.add(el.role_id)
    all_specializations = get_all_specializations()
    user_specializations_id = get_list_specialization_id(data_user)

    return {
        "id": data_user.id,
        "name": data_user.name,
        "telegram_id": data_user.telegram_id,
        "telegram": data_user.telegram,
        "phone": data_user.phone,
        "user_specializations_id": user_specializations_id,
        "all_specializations": all_specializations,
        "description": data_user.description,
        "role_id": role_id,
        "gmt": data_user.gmt,
        "gmt_sign": data_user.gmt_sign,
        "mentors_blocked": data_user.mentors_blocked
        }


def search_mentors(search_query, telegram_id, mentor_role_id):
    user_db = get_user_by_telegram(telegram_id)
    user_id = None
    if user_db:
        user_id = user_db.id
    search_query = search_query.lower()
    search_result = list()
    full_table = db_session.query(
        User.id.label("user_id"),
        User.name.label("user_name"),
        User.phone.label("user_phone"),
        User.telegram.label("user_telegram"),
        User.telegram_id.label("user_telegram_id"),
        User.description.label("user_description"),
        func.array_agg(Specialization.name).label("spec_name")
                                ).join(
                    UserSpecialization,
                    UserSpecialization.user_id == User.id
                                ).join(
                    Specialization,
                    UserSpecialization.specialization_id == Specialization.id
                                ).join(
                    UserRole,
                    UserRole.user_id == User.id
                                ).filter(
            ((User.name.ilike(f"%{search_query}%")) |
             (User.phone.ilike(f"%{search_query}%")) |
             (User.telegram.ilike(f"%{search_query}%")) |
             (User.description.ilike(f"%{search_query}%")) |
             (Specialization.name.ilike(f"%{search_query}%")))
            & (User.id != user_id) & (UserRole.role_id == mentor_role_id)
                                ).group_by(
                                            User.id, User.name,
                                            User.phone, User.telegram,
                                            User.description
                                          ).all()
    specials = db_session.query(
        Specialization.id.label("special_id"),
        Specialization.name.label("special_name"),
        UserSpecialization.user_id.label("user_id"),
        UserSpecialization.id.label("id")).join(
                    UserSpecialization,
                    UserSpecialization.specialization_id == Specialization.id
                    ).all()
    for row in full_table:
        user_specializations_name = [
            x.special_name for x in specials if x.user_id == row.user_id
                                    ]
        search_result.append({
            "mentor_id": row.user_id,
            "name": row.user_name,
            "telegram": row.user_telegram,
            "telegram_id": row.user_telegram_id,
            "phone": row.user_phone,
            "specializations": user_specializations_name,
            "description": row.user_description
            })
    return search_result


def get_list_dict_mentors(search_result_list_str):
    search_result = list()
    for search_result_str in search_result_list_str:
        search_result.append(ast.literal_eval(search_result_str))
    return search_result


def generate_time_list(start_time, end_time, interval_minutes):
    """
    Генерация временных интервалов.

    :param start_time: Время начала (строка в формате "HH:MM").
    :param end_time: Время окончания (строка в формате "HH:MM").
    :param interval_minutes: Длительность интервала в минутах.
    :return: Список временных интервалов.
    """
    intervals = []
    current_time = datetime.strptime(start_time, "%H:%M")
    end_time = datetime.strptime(end_time, "%H:%M")

    while current_time < end_time:
        next_time = current_time + timedelta(minutes=interval_minutes)
        intervals.append(
            f"{current_time.strftime('%H:%M')} - {next_time.strftime('%H:%M')}"
            )
        current_time = next_time

    return intervals


def get_my_calendar(telegram_id):
    events = list()
    cancel_status = Status.query.filter(Status.name == "cancel").first()

    all_events = db_session.query(
        TimeSlots.start_date_utc.label("start_date"),
        TimeSlots.end_date_utc.label("end_date"),
        TimeSlots.id.label("timeslot_id"),
        User.id.label("mentor_id"),
        User.telegram_id.label("mentor_telegram_id"),
        User.telegram.label("mentor_telegram"),
        User.name.label("mentor_name"),
        Events.id.label("event_id"),
        Events.request.label("request"),
        Events.client_id.label("client_id"),
        Events.status_id.label("status_id"),
        Status.name.label("status_name"),
        Client.telegram.label("client_telegram"),
        Client.telegram_id.label("client_telegram_id")
        ).outerjoin(
                    Events,
                    Events.slot_id == TimeSlots.id
        ).outerjoin(
                    Status,
                    Events.status_id == Status.id
        ).outerjoin(
                    Client,
                    Events.client_id == Client.id
        ).outerjoin(
                    User,
                    TimeSlots.user_id == User.id
                                 ).filter(
        (User.telegram_id == telegram_id) |
        (Client.telegram_id == telegram_id))
    canceled_events = (
        db_session.query(TimeSlots.id, Events.slot_id)
        .outerjoin(
                    Events,
                    and_(
                        Events.slot_id == TimeSlots.id,
                        Events.status_id == cancel_status.id
                        )
        )
        .outerjoin(User, TimeSlots.user_id == User.id)
        .outerjoin(Client, Events.client_id == Client.id)
        .filter(
            (User.telegram_id == telegram_id) |
            (Client.telegram_id == telegram_id)
        )
        .distinct()
    )
    canceled_events_list = [row.slot_id for row in canceled_events
                            if row.slot_id is not None]
    for i in range(len(canceled_events_list)):
        el = canceled_events_list[i]
        other_status = Events.query.filter(
                                        (Events.slot_id == el) &
                                        (Events.status_id != cancel_status.id)
                                          ).all()
        if other_status:
            canceled_events_list[i] = None
    canceled_events_list = [
                el for el in canceled_events_list if el is not None
                           ]
    cancel_avalaibale_events = db_session.query(
                TimeSlots.start_date_utc.label("start_date"),
                TimeSlots.end_date_utc.label("end_date"),
                TimeSlots.id.label("timeslot_id"),
                TimeSlots.user_id.label("mentor_id"),
                literal(None).label("mentor_telegram_id"),
                literal(None).label("mentor_telegram"),
                literal(None).label("mentor_name"),
                literal(None).label("event_id"),
                literal(None).label("request"),
                literal(None).label("client_id"),
                literal(None).label("status_id"),
                literal(None).label("status_name"),
                literal(None).label("client_telegram"),
                literal(None).label("client_telegram_id")
                            ).filter(TimeSlots.id.in_(canceled_events_list))
    query_events = union(
                            all_events,
                            cancel_avalaibale_events
                        ).alias("events_union")
    ordered_query_events = db_session.query(
        query_events).order_by(query_events.c.start_date)
    columns = [t["name"] for t in all_events.column_descriptions]
    for el in ordered_query_events.all():
        dict_events = dict()
        for i in range(len(columns)):
            dict_events[columns[i]] = el[i]
        events.append(dict_events)
    return events


def get_my_calendar_gmt(events, gmt, gmt_sign):
    if not gmt:
        return events
    if not isinstance(gmt, str):
        gmt = gmt.strftime("%H:%M")
    hours, minutes = map(int, gmt.split(":"))
    td = timedelta(hours=hours, minutes=minutes)
    for event in events:
        if gmt_sign == "-":
            event["start_date"] -= td
            event["end_date"] -= td
        else:
            event["start_date"] += td
            event["end_date"] += td
    return events


def get_mentor_timeslots_gmt(telegram_id, gmt, gmt_sign):
    mentor_db = get_user_data(telegram_id)
    timeslots_table = db_session.query(
                                TimeSlots.id.label("timeslot_id"),
                                TimeSlots.start_date_utc.label("start_date"),
                                TimeSlots.end_date_utc.label("end_date")
                                     ).outerjoin(
                                        Events,
                                        Events.slot_id == TimeSlots.id
                                     ).filter(
                                (TimeSlots.user_id == mentor_db.get("id")) &
                                (Events.slot_id == None))
    columns = [t["name"] for t in timeslots_table.column_descriptions]
    if not timeslots_table.all():
        return None
    hours, minutes = map(int, gmt.split(":"))
    td = timedelta(hours=hours, minutes=minutes)
    timeslots = list()
    for slot in timeslots_table.all():
        dict_slots = dict()
        for i in range(len(columns)):
            if columns[i] == "start_date" or columns[i] == "end_date":
                if gmt_sign == "-":
                    dict_slots[columns[i]] = slot[i] - td
                else:
                    dict_slots[columns[i]] = slot[i] + td
            else:
                dict_slots[columns[i]] = slot[i]
        timeslots.append(dict_slots)
    return timeslots


def get_date_set(telegram_id, gmt="00:00", gmt_sign="+"):
    set_date = set()
    timeslots = get_mentor_timeslots_gmt(telegram_id, gmt, gmt_sign)
    if not timeslots:
        return None
    for slot in timeslots:
        date = slot.get("start_date").date()
        date_str = date.strftime("%d-%m-%Y")
        set_date.add(date_str)
    return set_date


def get_time_set(telegram_id, gmt, gmt_sign, str_date):
    set_time = set()
    timeslots = get_mentor_timeslots_gmt(telegram_id, gmt, gmt_sign)
    if not timeslots:
        return None
    date = datetime.strptime(str_date, "%Y-%m-%d").date()
    for slot in timeslots:
        if slot.get("start_date").date() == date:
            start_time_str = slot.get("start_date").time().strftime("%H:%M")
            end_time_str = slot.get("end_date").time().strftime("%H:%M")
            set_time.add((str(slot.get("timeslot_id")) + "=" + start_time_str + "-"
                          + end_time_str))
    return set_time


def parcel_date_str(string):
    uniq_date_list = list()
    list_str = string.split(", ")
    for i in range(len(list_str)):
        list_str[i] = list_str[i].replace("{", "")
        list_str[i] = list_str[i].replace("}", "")
        list_str[i] = list_str[i].replace("'", "")
        date = datetime.strptime(list_str[i], "%d-%m-%Y").date()
        uniq_date_list.append(date)
    uniq_date_list.sort()
    return uniq_date_list


def parcel_time_str(string):
    uniq_time_list = list()
    string = string.replace("{", "")
    string = string.replace("}", "")
    string = string.replace("'", "")
    list_str = string.split(", ")
    for i in range(len(list_str)):
        id, time = list_str[i].split("=")
        uniq_time_list.append((int(id), time))
    uniq_time_list = sorted(uniq_time_list, key=lambda x: x[1])
    return uniq_time_list
