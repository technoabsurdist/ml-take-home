import os
import sys
import json
import time
import psutil
import subprocess
import tempfile
import importlib.util
import traceback
import concurrent.futures
from src.llm.openai import OpenAI
from memory_profiler import memory_usage
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

assert OPENAI_API_KEY is not None, "The OPENAI_API_KEY environment variable is not set."

MODEL = "gpt-4o-mini-2024-07-18"


def load_candidate_agent(agent_path: str):
    spec = importlib.util.spec_from_file_location("agent", agent_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load agent from {agent_path}")
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)
    return agent_module.Agent()


def run_script_with_io(script_content: str, input_str: str, timeout: int = 30):
    """
    Run the script_content as a Python script in a subprocess,
    feeding `input_str` to stdin. Capture stdout and stderr.
    Return (return_code, stdout, stderr).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        solution_path = os.path.join(tmpdir, "solution.py")
        with open(solution_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        # Run script, passing in the input via stdin
        cmd = [sys.executable, solution_path]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            stdout, stderr = proc.communicate(input=input_str, timeout=timeout)
            return proc.returncode, stdout, stderr
        except subprocess.TimeoutExpired:
            proc.kill()
            return 1, "", "Timed out"


def measure_resource_usage(func, *args, **kwargs):
    """
    Measure CPU time, memory usage, and wall-clock time while running `func`.
    Returns (func_return_value, resource_stats).
    """
    start_time = time.time()
    mem_usage = memory_usage((func, args, kwargs), interval=0.1, max_iterations=1)  # type: ignore
    cpu_time = psutil.Process().cpu_times().user
    result = func(*args, **kwargs)
    end_cpu_time = psutil.Process().cpu_times().user
    end_time = time.time()

    return result, {
        "cpu_time": end_cpu_time - cpu_time,
        "memory_usage_mb": max(mem_usage),
        "wall_clock_time": end_time - start_time,
    }


def process_single_question(item, agent, llm):
    """Process a single test question using the provided agent and LLM.
    
    Args:
        item: Dict containing the question and test cases
        agent: The loaded candidate agent
        llm: The OpenAI LLM instance
    
    Returns:
        Dict containing test results, including:
        - passed: Whether all tests passed
        - resources: Resource usage statistics
        - question: The original question
        - test_details: Details of individual test runs
        - error: Error message if an exception occurred
    """
    question = item.get("question", "")
    test_inputs = item.get("input", [])
    test_outputs = item.get("output", [])
    
    assert len(test_inputs) == len(test_outputs), "Input and output arrays must have the same length"
    
    try:
        # Get the candidate solution code with resource usage tracking
        script_content, resources = measure_resource_usage(
            agent.predict, llm, question
        )
        
        # Run each test case
        all_tests_passed = True
        individual_test_results = []
        
        for idx, input_str in enumerate(test_inputs):
            expected_output = test_outputs[idx]
            returncode, stdout, stderr = run_script_with_io(script_content, input_str)
            
            # Compare outputs (stripping trailing spaces/newlines)
            stdout_stripped = stdout.rstrip("\n")
            expected_stripped = expected_output.rstrip("\n")
            
            test_passed = returncode == 0 and stdout_stripped == expected_stripped
            if not test_passed:
                all_tests_passed = False
            
            individual_test_results.append({
                "test_index": idx,
                "input": input_str,
                "expected_output": expected_output,
                "actual_output": stdout,
                "passed": test_passed,
                "return_code": returncode,
                "stderr": stderr,
            })
        
        return {
            "question": question,
            "passed": all_tests_passed,
            "resources": resources,
            "test_details": individual_test_results,
        }
        
    except NotImplementedError:
        print(
            f"Agent.predict not implemented for question: {question}",
            file=sys.stderr,
        )
        return {
            "question": question,
            "passed": False,
            "error": "NotImplementedError"
        }
    except Exception:
        err = traceback.format_exc()
        return {
            "question": question,
            "passed": False,
            "error": err
        }


def main():
    test_dir = "/test_set"
    candidate_dir = "/candidate"

    if not os.path.exists(test_dir):
        print("Test directory not found.", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(candidate_dir):
        print("Candidate directory not found.", file=sys.stderr)
        sys.exit(1)

    # Load the list of questions/tests (which contain "input" and "output" arrays)
    questions_path = os.path.join(test_dir, "public_test.json")
    if not os.path.exists(questions_path):
        print("public_test.json not found.", file=sys.stderr)
        sys.exit(1)

    with open(questions_path, "r", encoding="utf-8") as f:
        test_info_list = json.load(f)

    agent_path = os.path.join(candidate_dir, "agent.py")
    if not os.path.exists(agent_path):
        print("Agent not found.", file=sys.stderr)
        sys.exit(1)

    # Load the candidate's agent
    agent = load_candidate_agent(agent_path)
    assert OPENAI_API_KEY is not None
    llm = OpenAI(model=MODEL, api_key=OPENAI_API_KEY)

    passed_count = 0
    total_questions = len(test_info_list)
    question_results = []

    # Process questions in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Submit all questions to the executor
        future_to_item = {
            executor.submit(process_single_question, item, agent, llm): item
            for item in test_info_list
        }
        
        # Process results as they complete, with progress bar
        for future in tqdm(
            concurrent.futures.as_completed(future_to_item),
            total=len(future_to_item),
            desc="Evaluating",
            unit="question"
        ):
            result = future.result()
            question_results.append(result)
            if result.get("passed", False):
                passed_count += 1

    final_score = passed_count / total_questions

    results = {
        "score": final_score,
        "total_questions": total_questions,
        "passed_count": passed_count,
    }

    with open("results.json", "w") as f:
        f.write(json.dumps(results | {"details": question_results}, indent=2))

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
