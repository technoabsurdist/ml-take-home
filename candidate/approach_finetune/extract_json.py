import pandas as pd
import json
import re

def clean_tags(tags):
    return re.sub(r',\*\d+', '', tags)

file_path = "./data.csv"
df = pd.read_csv(file_path)

df_subset = df.iloc[:500][['problem_statement', 'problem_tags']].copy()

df_subset['problem_tags'] = df_subset['problem_tags'].str.replace(r',\*\d+', '', regex=True)
df_subset['problem_tags'] = df_subset['problem_tags'].apply(lambda x: x.split(','))

json_data = df_subset.to_dict(orient="records")

json_file_path = "./problems_subset.json"
with open(json_file_path, "w") as json_file:
    json.dump(json_data, json_file, indent=4)
