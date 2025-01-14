from src.llm.core import BaseLLM
from src.agent import BaseAgent
from src.llm.core import TextChat
from src.llm.core import TextUserMessage
import os
from dotenv import load_dotenv

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
        chat = TextChat(
            system_prompt="You are a highly skilled software engineer.",
            messages=[TextUserMessage(content=PROMPT.format(question=question))],
        )
        raw_response = llm.predict(chat, max_tokens=1000, temperature=0.0)
        solution = raw_response.replace("```python", "").replace("```", "").strip()
        return solution
