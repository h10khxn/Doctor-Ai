import pandas as pd
df = pd.read_csv("data\dataset.csv")

data = []
unique_labels = df["Disease"].unique().tolist()
label2id = {label: idx for idx, label in enumerate(unique_labels)}

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    symptom_list = []
    

   


    # Loop through all columns except 'Disease'
    for col in df.columns:
        if col != "Disease":
            symptom = row[col]
            if pd.notna(symptom):  # Make sure symptom is not NaN
                symptom_list.append(symptom.strip())

    # Join all symptoms into a single string
    combined_symptoms = ", ".join(symptom_list)

    # Create a dictionary for this row
    sample = {
        "text": combined_symptoms,
        "label": label2id[row["Disease"]]
    }

    # Add to the main data list
    data.append(sample)



# Optionally print a few examples to verify
for item in data[:15]:
    print(item)