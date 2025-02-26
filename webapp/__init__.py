import logging
from webapp import settings_conf
from flask import Flask, render_template, request
from webapp.get_data import get_user_data
from webapp.profile.views import profile_blueprint
from webapp.calendar.views import calendar_blueprint
from webapp.mentors.views import mentors_blueprint


def create_app():

    app = Flask(__name__)
    homepage_title = "MentorMatch Calendar"
    app.register_blueprint(profile_blueprint)
    app.register_blueprint(calendar_blueprint)
    app.register_blueprint(mentors_blueprint)

    @app.route("/")
    def homepage():
        logger = logging.getLogger("error")
        logger.debug("starting HOMEPAGE")
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
    return app


app = create_app()
