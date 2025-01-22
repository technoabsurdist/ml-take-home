# LLM Interface Documentation

This document explains the core methods of the LLM interface in `candidate/src/llm/`.

## Core Methods

### predict(chat, max_tokens=1000, temperature=0.0)
- Generates a single response for a given chat
- Parameters:
  - `chat`: A TextChat object containing the conversation
  - `max_tokens`: Maximum length of the response
  - `temperature`: Controls randomness (0.0 = deterministic)
- Returns: String containing the model's response
- Includes automatic caching of responses

### sample(chat, max_tokens=1000, temperature=0.0, num_samples=1)
- Generates multiple responses for a given chat
- Parameters:
  - `chat`: A TextChat object containing the conversation
  - `max_tokens`: Maximum length of each response
  - `temperature`: Controls randomness
  - `num_samples`: Number of responses to generate
- Returns: List of response strings

### total_cost()
- Returns the total cost of API usage in USD based on prompt and completion tokens

## Message Structure

### TextChat
- Container for conversation messages
- Requires at least one message
- First message must be from user
- Optional system prompt for context
- Example:
```python
chat = TextChat(
    messages=[TextUserMessage(content="Hello")],
    system_prompt="Be helpful"  # Optional
)
```

## Basic Usage

```python
from src.llm.openai import OpenAI
from src.llm.core import TextChat, TextUserMessage

# Initialize
llm = OpenAI(model="gpt-3.5-turbo", api_key="your-key")

# Get single response
chat = TextChat(messages=[TextUserMessage(content="Hello")])
response = llm.predict(chat)

# Get multiple responses
samples = llm.sample(chat, num_samples=3)

# Check cost
cost = llm.total_cost()
