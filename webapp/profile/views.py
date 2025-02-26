from flask import (Blueprint, render_template, request, redirect, url_for)
from ..get_data import (get_user_data, generate_time_list)
from ..update_data import (change_data, check_username_and_update,
                           save_timeslots)
from webapp import settings_conf
from webapp.update_data import save_profile

profile_blueprint = Blueprint('profile', __name__, url_prefix='/my_profile')
homepage_title = "MentorMatch Calendar"


@profile_blueprint.route("/")
def my_profile():
    title = "My profile"
    telegram = request.args.get("telegram")
    telegram_id = int(request.args.get("telegram_id"))
    check_username_and_update(telegram, telegram_id)
    editing = request.args.get("editing", default=False, type=bool)
    user_db = get_user_data(telegram_id)
    role_id = set()
    if not user_db:
        return redirect(url_for("homepage", telegram=telegram,
                                telegram_id=telegram_id))
    name = user_db.get("name")
    role_id = user_db.get("role_id")
    return render_template("profile.html", editing=editing,
                           homepage=homepage_title,
                           mentor_role_id=settings_conf.MENTOR_ROLE_ID,
                           name=name, page_title=title, role_id=role_id,
                           telegram=telegram, telegram_id=telegram_id,
                           user_data=user_db)


@profile_blueprint.route("/actions", methods=["POST"])
def actions():
    request_form = request.form
    telegram = request_form.get("telegram")
    telegram_id = int(request_form.get("telegram_id"))
    action = request_form.get("action")
    if action == "edit":
        return redirect(url_for("profile.my_profile", editing=True,
                                telegram=telegram, telegram_id=telegram_id))
    elif action == "cancel":
        return redirect(url_for("profile.my_profile", telegram=telegram,
                                telegram_id=telegram_id))
    elif action == "submit":
        change_data(request_form)
    elif action == "create" or request_form.get("create_timeslot"):
        user_db = get_user_data(telegram_id)
        if not user_db:
            return redirect(url_for("profile.my_profile", telegram=telegram,
                                    telegram_id=telegram_id))
        title = "Time slots"
        successful_save = False
        mistake_save = False
        time_list = []
        name = user_db.get("name")
        role_id = user_db.get("role_id")
        if request_form.get("create_timeslot"):
            save = save_timeslots(request.form, user_db)
            if not save:
                mistake_save = True
            else:
                successful_save = True
        else:
            time_list = generate_time_list(settings_conf.START_TIME_SLOTS,
                                           settings_conf.END_TIME_SLOTS,
                                           settings_conf.INTERVAL_MINUTES)

        return render_template("timeslots.html", page_title=title,
                               telegram=telegram, telegram_id=telegram_id,
                               homepage=homepage_title, user_db=user_db,
                               time_list=time_list, name=name,
                               successful_save=successful_save,
                               mistake_save=mistake_save,
                               role_id=role_id,
                               mentor_role_id=settings_conf.MENTOR_ROLE_ID
                               )
    return redirect(url_for("profile.my_profile", telegram=telegram,
                            telegram_id=telegram_id))


@profile_blueprint.route("/mentors/mentors_registration", methods=["POST"])
def create_profile():
    telegram_id = int(request.form.get("telegram_id"))
    telegram = request.form.get("telegram")
    mentor_role_id = int(request.form.get("role_id"))
    save_profile(request.form)
    user_db = get_user_data(telegram_id)
    if user_db:
        role_id = user_db.get("role_id")
        if mentor_role_id in role_id:
            return redirect(url_for("homepage", mistake_creation="",
                                    successful_creation=True,
                                    telegram=telegram,
                                    telegram_id=telegram_id))
    return redirect(url_for("homepage", mistake_creation=True,
                            successful_creation="", telegram=telegram,
                            telegram_id=telegram_id))
