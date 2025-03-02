import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI()

# job = client.fine_tuning.jobs.create(
#     training_file="file-Whn5Zhh1bSNHPxbLW7hSmF",
#     model="gpt-4o-mini-2024-07-18",
#     suffix="test-extractor",
# )

# job_id = job.id
# print(f"Fine-tuning job created with ID: {job_id}")

job_name = "ftjob-n8ps55VtCHWK9V7uKf2qr6P9"

# Retrieve the state of the fine-tuning job
job = client.fine_tuning.jobs.retrieve(job_name)
print(f"Job status: {job.status}")

# model_name = job.fine_tuned_model
# print(f"Model name: {model_name}")
