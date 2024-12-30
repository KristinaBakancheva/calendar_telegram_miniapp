from db import db_session
from models import User_specialization
from .get_data import get_user_by_telegram, get_list_specialization_id


def check_username_and_update(telegram_username, telegram_id):
    user_db = get_user_by_telegram(telegram_id)
    if user_db and user_db.telegram != "@"+telegram_username:
        user_db.telegram = "@"+telegram_username
        db_session.commit()


def change_data(request_form):
    """
    The function updates ibformation in users and find outdated and new
    specializations for user
    """
    telegram_id = request_form.get("telegram_id")
    user_db = get_user_by_telegram(telegram_id)
    if hasattr(user_db, 'telegram') and user_db.telegram is not None:
        user_db.telegram = request_form.get("telegram")
    if hasattr(user_db, 'name') and user_db.name is not None:
        user_db.name = request_form.get("name")
    if hasattr(user_db, 'phone') and user_db.phone is not None:
        user_db.phone = request_form.get("phone")
    if hasattr(user_db, 'birthday') and user_db.birthday is not None:
        user_db.birthday = request_form.get("birthday")
    if hasattr(user_db, 'description') and user_db.description is not None:
        user_db.description = request_form.get("description")
    new_specializations = request_form.getlist("specialization")
    db_specializations_id = get_list_specialization_id(user_db)
    del_list = list()
    add_list = list()
    if hasattr(user_db, 'id') and user_db.id is not None:
        del_list = check_outdated_specialization(
            user_db.id, new_specializations, db_specializations_id)
        add_list = check_new_specialization(
            user_db.id, new_specializations)
        for el in del_list:
            db_session.delete(el)
        for el in add_list:
            db_session.add(el)
        db_session.commit()


def create_user(user_id, user_specialization_id):
    """
    The function creates new pair user_id and specialization_id
    for class User_specialization
    """
    user_special = User_specialization.query.filter(
        User_specialization.user_id == user_id,
        User_specialization.specialization_id ==
        user_specialization_id).first()
    return user_special


def check_outdated_specialization(user_id, new_specializations,
                                  db_specializations):
    del_list = list()
    for user_specialization in db_specializations:
        if str(user_specialization) not in new_specializations:
            user_special = create_user(
                user_id, user_specialization)
            del_list.append(user_special)
    return del_list


def check_new_specialization(user_id, new_specializations):
    add_list = list()
    for specialization_id in new_specializations:
        specialization_id = int(specialization_id)
        user_special = create_user(user_id, specialization_id)
        if not user_special:
            new_user_special = User_specialization(
                user_id=user_id, specialization_id=specialization_id)
            add_list.append(new_user_special)
    return add_list
