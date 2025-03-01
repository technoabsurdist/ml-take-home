from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

# job = client.fine_tuning.jobs.create(
#     training_file="file-632nWxLXHVaqhPjxp5CcMc",
#     model="gpt-4o-mini-2024-07-18",
#     suffix="test-extractor",
# )

# job_id = job.id
# print(f"Fine-tuning job created with ID: {job_id}")

# Retrieve the state of the fine-tuning job
job = client.fine_tuning.jobs.retrieve("ftjob-sPhbBOxUXOm0fsWQAkQ3NsOk")
print(f"Job status: {job.status}")

# The model name will be available in the job details
job = client.fine_tuning.jobs.retrieve("ftjob-sPhbBOxUXOm0fsWQAkQ3NsOk")
model_name = job.fine_tuned_model
print(f"Model name: {model_name}")
