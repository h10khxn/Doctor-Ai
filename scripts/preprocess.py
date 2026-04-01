import pandas as pd
from datasets import Dataset, DatasetDict
from transformers import AutoTokenizer


df = pd.read_csv("data/dataset.csv")


data = []
unique_labels = df["Disease"].unique().tolist()
label2id = {label: idx for idx, label in enumerate(unique_labels)}

for _, row in df.iterrows():
    symptom_list = []

    # Collect nonemptys ymptoms
    for col in df.columns:
        if col != "Disease":
            symptom = row[col]
            if pd.notna(symptom):
                symptom_list.append(symptom.strip())

    combined_symptoms = ", ".join(symptom_list)

    sample = {
        "text": combined_symptoms,
        "label": label2id[row["Disease"]]
    }

    data.append(sample)


for item in data[:15]:
    print(item)

# Use full dataset for training (no held-out split)
raw_dataset = Dataset.from_list(data)
dataset_dict = DatasetDict({
    "train": raw_dataset,
    "validation": raw_dataset,
})

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

# Tokenization function
def tokenize_function(example):
    return tokenizer(example["text"], padding="max_length", truncation=True, max_length=64)


tokenized_dataset = dataset_dict.map(tokenize_function, batched=True)

# Save processed dataset
tokenized_dataset.save_to_disk("data/processed_dataset")
