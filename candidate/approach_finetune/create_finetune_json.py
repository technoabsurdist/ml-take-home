import json

input_json_file = "./problems_subset.json"
output_jsonl_file = "./problems_finetune.jsonl"

with open(input_json_file, "r") as f:
    data = json.load(f)

system_instruction = {
    "role": "system",
    "content": "You are a helpful assistant that assigns problem tags to problem statements."
}

with open(output_jsonl_file, "w") as f:
    for item in data:
        entry = {
            "messages": [
                system_instruction,
                {"role": "user", "content": item["problem_statement"]},
                {"role": "assistant", "content": ", ".join(item["problem_tags"])}
            ]
        }
        f.write(json.dumps(entry) + "\n")
