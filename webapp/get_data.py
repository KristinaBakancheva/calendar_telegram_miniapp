from models import User, Specialization, User_specialization, Role


def get_user_role(role_id):
    """
    The function returns role's name or "" use role_id
    """
    role_db = Role.query.filter(Role.id == role_id).first()
    if role_db:
        return role_db.name
    else:
        return ""


def get_all_specializations():
    """
    The function returns list of pair name and id of all specializations
    from database
    """

    all_specializations = list()
    for specialization in Specialization.query.all():
        if (
            hasattr(specialization, 'name') and specialization.name is not None
            and hasattr(specialization, 'id') and specialization.id is not None
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
    data = User.query.filter(User.telegram_id == telegram_id).all()
    if data:
        return data[0]
    else:
        return None  # !!!!! Как правильно обработать такую ошибку?


def get_list_specialization_id(user_data):
    """
    The function returns all specialization_id for user_data.id
    """
    user_specializations_id = list()
    if hasattr(user_data, 'id') and user_data.id is not None:
        user_specializations = User_specialization.query.filter(
            User_specialization.user_id == user_data.id).all()
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
    all_specializations = get_all_specializations()
    user_specializations_id = get_list_specialization_id(data_user)

    return {
        "name": data_user.name,
        "telegram_id": data_user.telegram_id,
        "telegram": data_user.telegram,
        "birthday": data_user.birthday,
        "phone": data_user.phone,
        "user_specializations_id": user_specializations_id,
        "all_specializations": all_specializations,
        "description": data_user.description,
        "role_id": data_user.role_id
        }
