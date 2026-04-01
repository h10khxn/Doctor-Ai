import json
from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from app.extensions import db
from app.models import PredictionHistory
from app import csrf
from scripts.predict import predict, extract_symptoms, symptom_list, symptom_readable
from scripts.camera_predict import predict_from_image_b64

routes = Blueprint("routes", __name__)

symptoms_display = [{"key": s, "label": symptom_readable[s].title()} for s in symptom_list]


@routes.route("/")
def index():
    return render_template("index.html", symptoms=symptoms_display)


@routes.route("/predict", methods=["POST"])
@csrf.exempt
def predict_route():
    data = request.get_json()
    mode = data.get("mode")
    symptom_text = ""

    if mode == "checkbox":
        symptom_text = ", ".join(data.get("symptoms", []))
    elif mode == "nlp":
        symptom_text = extract_symptoms(data.get("text", ""))

    if not symptom_text:
        return jsonify({"error": "No symptoms detected. Please select symptoms or describe them more specifically."}), 400

    results = predict(symptom_text)
    _save_history(mode, symptom_text, results)
    return jsonify({"results": results, "matched_symptoms": symptom_text})


@routes.route("/predict-image", methods=["POST"])
@csrf.exempt
def predict_image_route():
    data = request.get_json()
    b64 = data.get("image", "")
    if not b64:
        return jsonify({"error": "No image data received."}), 400

    img_result = predict_from_image_b64(b64)
    if "error" in img_result:
        return jsonify(img_result), 400

    results = predict(img_result["symptoms"])
    _save_history("camera", img_result["symptoms"], results)
    return jsonify({
        "results": results,
        "matched_symptoms": img_result["symptoms"],
        "image_label": img_result["image_label"],
        "image_confidence": img_result["confidence"],
    })


def _save_history(mode: str, symptoms: str, results: list):
    if current_user.is_authenticated and results:
        record = PredictionHistory(
            user_id=current_user.id,
            input_mode=mode,
            matched_symptoms=symptoms,
            top_disease=results[0]["disease"],
            top_confidence=results[0]["confidence"],
            full_results_json=json.dumps(results),
        )
        db.session.add(record)
        db.session.commit()
