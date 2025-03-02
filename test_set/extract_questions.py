import json

with open("test_set/public_test.json", "r") as f:
    data = json.load(f)

questions = []
for question in data:
    questions.append(question["question"])

with open("questions.json", "w") as f:
    json.dump(questions, f, indent=4)

print(f"Successfully extracted {len(questions)} questions to questions.json")
