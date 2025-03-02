import json
import os

from dotenv import load_dotenv
from eval import check_correctness
from src.agent import BaseAgent
from src.llm.core import BaseLLM, TextChat, TextUserMessage
from src.llm.openai import OpenAI

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

assert openai_api_key is not None, "The OPENAI_API_KEY environment variable is not set."

PROMPT = """You are a Python coding assistant tasked with solving programming challenges. Your goal is to provide a \
correct, efficient, and readable Python solution to the following coding question:

<coding_question>
{question}
</coding_question>

Instructions:
1. Before implementing the solution, analyze the problem in <problem_analysis> tags:
   - Break down the problem into smaller steps
   - Plan your approach to solving each step
   - Consider potential edge cases and how to handle them
   - Identify any key algorithms or data structures you'll use
2. Implement a complete, runnable Python script that solves the given problem.
3. Use Python 3 syntax.
4. Optimize for both readability and efficiency.
5. Handle input and output as specified in the question, typically reading from stdin and writing to stdout.
6. Include brief comments to explain key parts of your code.
7. Do not include any explanations or additional text outside of the Python code itself.
8. If you have made previous attempts to solve the problem, and they failed, please analyze the failures and write a new solution that addresses the failures.

Remember:
- Your solution will be graded automatically, so adhere strictly to the input/output requirements.
- Only output the Python code; do not include any additional formatting or explanations.

Now, please provide your Python solution to the coding question.
""".strip()


class Agent(BaseAgent):
    def predict(self, llm: BaseLLM, question: str) -> str:
        tests_info = self.extract_tests(question)

        chat = TextChat(
            system_prompt="You are a highly skilled software engineer.",
            messages=[TextUserMessage(content=PROMPT.format(question=question))],
        )
        raw_response = llm.predict(chat, max_tokens=1000, temperature=0.0)
        solution = raw_response.replace("```python", "").replace("```", "").strip()

        failed_results = []
        for test in tests_info["tests"]:
            input = test["input"]
            output = test["output"]
            result = check_correctness(solution, input, output, 2)
            if result != "passed":
                failed_results.append(result)

        retry_count = 0
        max_retries = 5

        solution_history = []
        if failed_results:
            solution_history.append(
                {"attempt": 1, "solution": solution, "failures": failed_results.copy()}
            )

        while failed_results and retry_count < max_retries:
            history_prompt = "You've made previous attempts to solve this problem, but they failed to pass some tests.\n\n"

            for i, attempt in enumerate(solution_history):
                history_prompt += (
                    f"ATTEMPT #{i + 1}:\n```python\n{attempt['solution']}\n```\n\n"
                )
                history_prompt += f"FAILURES FOR ATTEMPT #{i + 1}:\n"
                history_prompt += "\n".join(attempt["failures"]) + "\n\n"

            chat = TextChat(
                system_prompt="You are a highly skilled software engineer.",
                messages=[
                    TextUserMessage(
                        content=f"{history_prompt}\n\n{PROMPT.format(question=question)}"
                    )
                ],
            )
            raw_response = llm.predict(chat, max_tokens=1000, temperature=0.0)
            solution = raw_response.replace("```python", "").replace("```", "").strip()

            failed_results = []
            for test in tests_info["tests"]:
                input = test["input"]
                output = test["output"]
                result = check_correctness(solution, input, output, 2)
                if result != "passed":
                    failed_results.append(result)

            retry_count += 1
            if failed_results:
                solution_history.append(
                    {
                        "attempt": retry_count + 1,
                        "solution": solution,
                        "failures": failed_results.copy(),
                    }
                )

        return solution

    def extract_tests(self, question: str) -> list:
        test_extractor_llm = OpenAI(
            model="ft:gpt-4o-mini-2024-07-18:elicit-experiments:test-extractor:B6KAXvuu",
            api_key=openai_api_key,
        )

        chat = TextChat(
            system_prompt="You are an AI assistant that extracts test cases from competitive programming problems. Always return the result as a valid JSON object with fields for 'num_tests' and an array of 'tests' containing input/output pairs.",
            messages=[TextUserMessage(content=question)],
        )
        raw_response = test_extractor_llm.predict(
            chat, max_tokens=2000, temperature=0.2
        )
        tests_info = json.loads(raw_response)
        return tests_info
