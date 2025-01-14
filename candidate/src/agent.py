from abc import ABC, abstractmethod
from src.llm.core import BaseLLM


class BaseAgent(ABC):

    @abstractmethod
    def predict(self, llm: BaseLLM, question: str) -> str:
        """Implement the solution code generation logic for your agent. The solution code
        should be in Python with inputs given via stdin and outputs printed to stdout. E.g.:

            ```
            my_input = input() # Read input from stdin
            my_answer = my_input * 2
            print(my_answer) # Print the answer to stdout
            ```
        """
        ...
