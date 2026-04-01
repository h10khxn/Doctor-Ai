import torch
import pandas as pd
from rapidfuzz import process, fuzz
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "models/doctor_model"
DATA_PATH = "data/dataset.csv"
DESC_PATH = "data/symptom_Description.csv"
PRECAUTION_PATH = "data/symptom_precaution.csv"
SYMPTOM_PATH = "data/Symptom-severity.csv"

# Load once at import time
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

df = pd.read_csv(DATA_PATH)
id2label = {idx: label for idx, label in enumerate(df["Disease"].unique().tolist())}

desc_df = pd.read_csv(DESC_PATH).set_index("Disease")
precaution_df = pd.read_csv(PRECAUTION_PATH).set_index("Disease")

symptom_list = pd.read_csv(SYMPTOM_PATH)["Symptom"].str.strip().tolist()
symptom_readable = {s: s.replace("_", " ") for s in symptom_list}

# rapidfuzz lookup: readable label -> canonical symptom key
_readable_to_key = {symptom_readable[s]: s for s in symptom_list}
_all_readable = list(_readable_to_key.keys())


def predict(symptom_text: str, top_k: int = 3) -> list:
    inputs = tokenizer(symptom_text, return_tensors="pt", padding="max_length", truncation=True, max_length=64)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1)[0]
    top_probs, top_indices = torch.topk(probs, top_k)

    results = []
    for prob, idx in zip(top_probs.tolist(), top_indices.tolist()):
        disease = id2label[idx]
        description = desc_df.loc[disease, "Description"] if disease in desc_df.index else ""
        precautions = []
        if disease in precaution_df.index:
            row = precaution_df.loc[disease]
            precautions = [row[c] for c in precaution_df.columns if pd.notna(row[c]) and row[c] != ""]
        results.append({
            "disease": disease,
            "confidence": round(prob * 100, 1),
            "description": description,
            "precautions": precautions,
        })
    return results


def extract_symptoms(text: str) -> str:
    text_lower = text.lower()
    matched_keys = set()
    results = process.extract(
        text_lower,
        _all_readable,
        scorer=fuzz.token_set_ratio,
        score_cutoff=80,
        limit=None,
    )
    for readable, score, _ in results:
        matched_keys.add(_readable_to_key[readable])
    return ", ".join(sorted(matched_keys))
