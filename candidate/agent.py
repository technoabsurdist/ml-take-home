import json
import os

from dotenv import load_dotenv
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

Remember:
- Your solution will be graded automatically, so adhere strictly to the input/output requirements.
- Only output the Python code; do not include any additional formatting or explanations.

Now, please provide your Python solution to the coding question.
""".strip()


class Agent(BaseAgent):

    def predict(self, llm: BaseLLM, question: str) -> str:
        # extrac tests
        tests_info = self.extract_tests(question)

        # generate solution
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
        
        while failed_results and retry_count < max_retries:
            print(f"Retrying {retry_count + 1} time(s)")
            failed_tests_info = "\n".join(failed_results)
            enhanced_question = f"""
You've previously written a solution to this problem, but it failed to pass some tests.

Fix the issues in your solution.

PREVIOUS ATTEMPT:
```python
{solution}
```

TEST FAILURES:
{failed_tests_info}

Please fix these issues in your solution."""
            
            chat = TextChat(
                system_prompt="You are a highly skilled software engineer.",
                messages=[TextUserMessage(content=f"{enhanced_question}\n\n{PROMPT.format(question=question)}")],
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
            
            print(TextUserMessage(content=f"{enhanced_question}\n\n{PROMPT.format(question=question)}"))
            print("--------------------------------\n\n\n")
            print("failed test results: ", len(failed_results))
            print("--------------------------------\n\n\n")
 
            retry_count += 1
        
        return solution

    def extract_tests(self, question: str) -> list:
        test_extractor_llm = OpenAI(
            model="ft:gpt-4o-mini-2024-07-18:elicit-experiments:test-extractor:B6KAXvuu",
            api_key=openai_api_key,
        )

        chat = TextChat(
            system_prompt="You are an AI assistant that extracts test cases from competitive programming problems. Always return the result as a valid JSON object with fields for 'num_tests' and an array of 'tests' containing input/output pairs.",
            messages=[
                TextUserMessage(
                    content=question
                )
            ],
        )
        raw_response = test_extractor_llm.predict(
            chat, max_tokens=2000, temperature=0.2
        )
        tests_info = json.loads(raw_response)
        return tests_info 




###### EVALUATION CODE
# WARNING
# This program would not be safe to run in a production environment.
# It is designed to be run in a sandboxed environment.
# it is highly unlikely that model-generated code will do something overtly
# malicious in response to this test suite, model-generated code may act
# destructively due to a lack of model capability or alignment.

import multiprocessing
import queue
import subprocess
import sys
import time
import traceback

multiprocessing.set_start_method("fork", force=True)

def exec_program(q, program, input_data, expected_output, timeout):
    try:
        start_time = time.time()
        process = subprocess.Popen(
            [sys.executable, "-c", program],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(input=input_data, timeout=timeout)
        if time.time() - start_time > timeout:
            raise TimeoutError("Execution timed out.")
        if process.returncode != 0:
            q.put(f"failed: {stderr}")
        else:
            if stdout.strip() == expected_output.strip():
                q.put("passed")
            else:
                q.put(f"wrong answer. Expected '{expected_output}', got '{stdout}'")
    except subprocess.TimeoutExpired:
        process.kill()
        q.put("timed out")
    except Exception:
        q.put(f"failed: {traceback.format_exc()}")


def check_correctness(
    program: str, input_data: str, expected_output: str, timeout: float
) -> str:
    q = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=exec_program, args=(q, program, input_data, expected_output, timeout)
    )
    process.start()
    process.join(timeout=timeout + 1)
    if process.is_alive():
        process.terminate()
        process.join()
        result = "timed out"
    else:
        try:
            result = q.get_nowait()
        except queue.Empty:
            result = "no result returned"
    return result