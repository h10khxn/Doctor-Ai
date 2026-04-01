from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email         = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    predictions   = db.relationship("PredictionHistory", backref="user", lazy="dynamic",
                                    cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class PredictionHistory(db.Model):
    __tablename__ = "prediction_history"
    id                = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    input_mode        = db.Column(db.String(20), nullable=False)
    matched_symptoms  = db.Column(db.Text, nullable=False)
    top_disease       = db.Column(db.String(120), nullable=False)
    top_confidence    = db.Column(db.Float, nullable=False)
    full_results_json = db.Column(db.Text, nullable=False)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow, index=True)
