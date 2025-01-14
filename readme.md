# LLM Coding Agent Challenge

## Overview

This coding challenge tests your ability to create a coding agent that leverage LLMs to generate Python code solutions. Your task is to implement an agent that can understand problem descriptions and generate correct Python code solutions using the provided LLM interface.

## Challenge Structure

- You will implement the `predict` method in a class that inherits from `BaseAgent`
- Your agent will receive questions and must generate Python code solutions
- Solutions will be tested against multiple test cases with input/output validation
- The LLM (GPT-4o mini) is provided through a standard interface

## Requirements

### Agent Implementation

```python
def predict(self, llm: BaseLLM, question: str) -> str:
    """
    Implement your solution generation logic here.

    Args:
        llm: The LLM interface to use for generating solutions
        question: The problem description

    Returns:
        str: Python code that solves the given problem
    """
```

### Solution Format

Your agent should return Python code that:

- Reads input from stdin using `input()`
- Processes the input according to the problem requirements
- Prints the solution to stdout using `print()`

Example solution format:

```python
# Read input
user_input = input()

# Process input and generate solution
result = process_input(user_input)

# Output solution
print(result)
```

## Evaluation Criteria

### Correctness

- Solutions must produce correct output for all test cases
- Each solution must complete within 30 seconds
- Solutions must handle edge cases appropriately

### Code Quality

- Your agent implementation should be well-structured and maintainable
- Include appropriate error handling
- Add comments to explain complex logic
- Follow Python best practices and PEP 8 style guidelines

### LLM Integration

- Effective use of the provided LLM interface
- Appropriate prompt engineering and response handling
- Efficient use of LLM calls

## Testing Environment

- Solutions will be run in a containerized environment
- Standard Python libraries are available
- You're welcome to run LLM-generated code if helpful
- Resource usage (CPU time, memory) will be monitored

## Setup

1. Install Docker: https://docs.docker.com/get-docker/
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Add an OpenAI API key to a `.env` file (see `.env.example`).
4. Run the test runner:
   ```bash
    ./run.sh
   ```
5. Verify that the test runner executes successfully (note that the agent won't pass the tests initially)

## Getting Started

1. Modify the file `agent.py` in the `candidate` directory
2. Implement your agent class inheriting from `BaseAgent`
3. Implement the `predict` method
4. Test your implementation using the provided test runner:
   ```bash
   ./run.sh
   ```

## Example Usage

````python
from base_agent import BaseAgent

class Agent(BaseAgent):
    def predict(self, llm: BaseLLM, question: str) -> str:
        # Your implementation here
        # Use the LLM to generate appropriate Python code
        chat = TextChat(
            system_prompt="You are a highly skilled software engineer.",
            messages=[
                TextUserMessage(content=PROMPT.format(question=question))
            ]
        )
        raw_response = llm.predict(chat, max_tokens=1000, temperature=0.0)
        solution = raw_response.replace("```python", "").replace("```", "").strip()
        return solution
````

## Submission

- Ensure your code is in the correct location (`candidate/agent.py`)
- Verify it runs successfully with the provided test runner
- Include a short write-up explaining your approach and any trade-offs in a file named `writeup.md`
