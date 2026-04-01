import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from app.extensions import db, login_manager

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        app.instance_path, "mini_doctor.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes import routes
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.history.routes import history_bp
    from app.blueprints.pages.routes import pages_bp

    app.register_blueprint(routes)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(history_bp, url_prefix="/history")
    app.register_blueprint(pages_bp)

    with app.app_context():
        db.create_all()

    return app
