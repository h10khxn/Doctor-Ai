import base64
import io
from PIL import Image
from transformers import pipeline

IMAGE_MODEL_ID = "Anwarkh1/Skin_Cancer-Image_Classification"
CONFIDENCE_THRESHOLD = 0.40

_image_pipe = None


def get_image_pipeline():
    global _image_pipe
    if _image_pipe is None:
        _image_pipe = pipeline("image-classification", model=IMAGE_MODEL_ID)
    return _image_pipe


# Maps image model labels -> symptom keys from Symptom-severity.csv
IMAGE_LABEL_TO_SYMPTOMS = {
    # Anwarkh1/Skin_Cancer-Image_Classification labels
    "melanoma":                        ["skin_rash", "dischromic_patches", "nodal_skin_eruptions"],
    "melanocytic_nevi":                ["skin_rash", "nodal_skin_eruptions"],
    "melanocytic nevi":                ["skin_rash", "nodal_skin_eruptions"],
    "benign_keratosis-like_lesions":   ["skin_rash", "itching", "nodal_skin_eruptions"],
    "benign keratosis-like lesions":   ["skin_rash", "itching", "nodal_skin_eruptions"],
    "basal_cell_carcinoma":            ["skin_rash", "nodal_skin_eruptions"],
    "basal cell carcinoma":            ["skin_rash", "nodal_skin_eruptions"],
    "actinic_keratoses":               ["skin_rash", "itching", "skin_peeling"],
    "actinic keratoses":               ["skin_rash", "itching", "skin_peeling"],
    "vascular_lesions":                ["skin_rash"],
    "vascular lesions":                ["skin_rash"],
    "dermatofibroma":                  ["skin_rash", "nodal_skin_eruptions"],
    "squamous_cell_carcinoma":         ["skin_rash", "nodal_skin_eruptions", "skin_peeling"],
    "squamous cell carcinoma":         ["skin_rash", "nodal_skin_eruptions", "skin_peeling"],
}


def predict_from_image_b64(b64_string: str) -> dict:
    try:
        if "," in b64_string:
            b64_string = b64_string.split(",", 1)[1]
        image_bytes = base64.b64decode(b64_string)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        return {"error": f"Invalid image data: {e}"}

    try:
        pipe = get_image_pipeline()
        results = pipe(image, top_k=3)
    except Exception as e:
        return {"error": f"Image analysis failed: {e}"}

    top = [r for r in results if r["score"] >= CONFIDENCE_THRESHOLD]
    if not top:
        return {"error": "Image confidence too low. Please use a clearer photo or describe symptoms manually."}

    collected = []
    for result in top:
        label_key = result["label"].lower().replace(" ", "_")
        for s in IMAGE_LABEL_TO_SYMPTOMS.get(label_key, []):
            if s not in collected:
                collected.append(s)

    if not collected:
        return {"error": f"Detected '{top[0]['label']}' but could not map to known symptoms. Try describing symptoms manually."}

    return {
        "symptoms": ", ".join(collected),
        "image_label": top[0]["label"],
        "confidence": round(top[0]["score"] * 100, 1),
    }
