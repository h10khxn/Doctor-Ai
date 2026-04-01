import json
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import PredictionHistory

history_bp = Blueprint("history", __name__)


@history_bp.route("/")
@login_required
def index():
    records = (PredictionHistory.query
               .filter_by(user_id=current_user.id)
               .order_by(PredictionHistory.created_at.desc())
               .limit(50)
               .all())
    for r in records:
        r.results = json.loads(r.full_results_json)
    return render_template("history/index.html", records=records)
