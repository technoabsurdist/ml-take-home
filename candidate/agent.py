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

EXTRACT_TESTS_PROMPT = """You are an AI assistant that extracts test cases from competitive programming problems. \
Always return the result as a valid JSON object with fields for 'num_tests' and an array of 'tests' containing input/output pairs."""

REASON_FOR_FAILURE_PROMPT = """You are an experienced software engineer analyzing a failed coding solution. 
Your task is to determine why the solution failed specific test cases and provide a concise explanation.

<coding_question>
{question}
</coding_question>

<coding_solution>
{solution}
</coding_solution>

Failed Test Cases:

<failures>
{failed_results}
</failures>

Analyze the provided question, solution, and failed test cases. Identify the root cause of failure in a direct, 
1-3 sentence explanation. Clearly specify any logical errors, incorrect assumptions, edge cases not handled, or inefficiencies leading to failure.
""".strip()


class Agent(BaseAgent):
    def predict(self, llm: BaseLLM, question: str) -> str:
        tests_info = self.extract_tests(question)
        solution = self._generate_initial_solution(llm, question)

        failed_results = self._evaluate_solution(solution, tests_info)
        solution_history = []

        if failed_results:
            reason_for_failure = self._generate_reason_for_failure(llm, question, solution, failed_results)
            solution_history.append(
                {"attempt": 1, "solution": solution, "failures": failed_results.copy(), "reason_for_failure": reason_for_failure}
            )

            solution = self._iterative_refinement(
                llm, question, solution_history, tests_info
            )

        return solution

    def _generate_initial_solution(self, llm: BaseLLM, question: str) -> str:
        chat = TextChat(
            system_prompt="You are a highly skilled software engineer.",
            messages=[TextUserMessage(content=PROMPT.format(question=question))],
        )
        raw_response = llm.predict(chat, max_tokens=1000, temperature=0.0)
        return raw_response.replace("```python", "").replace("```", "").strip()

    def _evaluate_solution(self, solution: str, tests_info: dict) -> list:
        failed_results = []
        for test in tests_info["tests"]:
            input = test["input"]
            output = test["output"]
            result = check_correctness(solution, input, output, 4)
            if result != "passed":
                failed_results.append(result)
        return failed_results

    def _generate_reason_for_failure(self, llm: BaseLLM, question: str, solution: str, failed_results: list) -> str:
        chat = TextChat(
            system_prompt="You are a highly skilled software engineer.",
            messages=[
                TextUserMessage(content=REASON_FOR_FAILURE_PROMPT.format(question=question, solution=solution, failed_results=failed_results))
            ],
        )
        return llm.predict(chat, max_tokens=1000, temperature=0.0)

    def _iterative_refinement(
        self, llm: BaseLLM, question: str, solution_history: list, tests_info: dict
    ) -> str:
        retry_count = 0
        max_retries = 5

        while retry_count < max_retries:
            history_prompt = self._build_history_prompt(solution_history)

            solution = self._generate_refined_solution(llm, question, history_prompt)

            failed_results = self._evaluate_solution(solution, tests_info)


            if not failed_results:
                break

            reason_for_failure = self._generate_reason_for_failure(llm, question, solution, failed_results)

            retry_count += 1
            solution_history.append(
                {
                    "attempt": retry_count + 1,
                    "solution": solution,
                    "failures": failed_results.copy(),
                    "reason_for_failure": reason_for_failure,
                }
            )

        return solution

    def _build_history_prompt(self, solution_history: list) -> str:
        history_prompt = "You've made previous attempts to solve this problem, but they failed to pass some tests.\n\n"

        for i, attempt in enumerate(solution_history):
            history_prompt += (
                f"ATTEMPT #{i + 1}:\n```python\n{attempt['solution']}\n```\n\n"
            )
            history_prompt += f"FAILURES FOR ATTEMPT #{i + 1}:\n"
            history_prompt += "\n".join(attempt["failures"]) + "\n\n"
            history_prompt += f"REASON FOR FAILURE FOR ATTEMPT #{i + 1}:\n"
            history_prompt += f"{attempt['reason_for_failure']}\n\n"


        print("-" * 80)
        print("HISTORY PROMPT:")
        print(history_prompt)
        print("-" * 80)

        return history_prompt

    def _generate_refined_solution(
        self, llm: BaseLLM, question: str, history_prompt: str
    ) -> str:
        """Generate a refined solution based on previous attempts."""
        chat = TextChat(
            system_prompt="You are a highly skilled software engineer.",
            messages=[
                TextUserMessage(
                    content=f"{history_prompt}\n\n{PROMPT.format(question=question)}"
                )
            ],
        )
        raw_response = llm.predict(chat, max_tokens=1000, temperature=0.0)
        return raw_response.replace("```python", "").replace("```", "").strip()

    def extract_tests(self, question: str) -> list:
        test_extractor_llm = OpenAI(
            model="ft:gpt-4o-mini-2024-07-18:elicit-experiments:test-extractor:B6KAXvuu",
            api_key=openai_api_key,
        )

        chat = TextChat(
            system_prompt=EXTRACT_TESTS_PROMPT,
            messages=[TextUserMessage(content=question)],
        )
        raw_response = test_extractor_llm.predict(
            chat, max_tokens=2000, temperature=0.2
        )
        tests_info = json.loads(raw_response)
        return tests_info
