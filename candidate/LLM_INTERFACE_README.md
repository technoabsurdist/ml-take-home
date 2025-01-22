# LLM Interface Documentation

This document describes the LLM interface implementation found in `candidate/src/llm/`. The interface provides a flexible and extensible way to interact with Large Language Models, with built-in support for OpenAI's models.

## Architecture Overview

The LLM interface consists of two main components:

1. **Base Abstract Class (`core.py`)**: Defines the interface contract and common functionality
2. **OpenAI Implementation (`openai.py`)**: Provides concrete implementation for OpenAI models

### BaseLLM Abstract Class

The `BaseLLM` class in `core.py` serves as the foundation for all LLM implementations. It provides:

- Abstract methods that must be implemented by concrete classes:
  - `_predict()`: Generate a single completion
  - `_sample()`: Generate multiple completions
  - `total_cost()`: Calculate usage costs
  - `model_name()`: Get the name of the model

- Built-in features:
  - SQLite-based response caching
  - Cost tracking
  - Standardized interface for both chat and completion

### Message Structure and Validation

The interface uses Pydantic models to ensure proper message structure:

- `TextUserMessage`: Messages from the user
- `TextAssistantMessage`: Messages from the assistant
- `TextChat`: Container for conversation history that enforces:
  - At least one message must be present
  - First message must be from the user
  - Consecutive messages must alternate between user and assistant
  - Optional system prompt support

## OpenAI Implementation

The `OpenAI` class in `openai.py` implements the `BaseLLM` interface for OpenAI models. Features include:

- Support for various GPT models
- Configurable settings:
  - Maximum retries
  - Timeout duration
  - Temperature
  - Maximum tokens
- Token usage tracking
- Model-specific cost calculation

### Cost Tracking

The implementation tracks costs based on the model used:
- GPT-3.5 Turbo
- GPT-4
- Custom variants (e.g., GPT-4-mini)

Costs are calculated based on both prompt and completion tokens.

## Key Features

### Caching System

The interface includes an SQLite-based caching system that:
- Stores responses to avoid redundant API calls
- Uses a hash of the entire conversation as the cache key
- Supports both single predictions and multiple samples
- Persists across sessions

### Message Validation

The interface enforces strict message validation:
- Proper message order
- Role alternation
- Required user first message
- Optional system prompt support

## Usage Requirements

### Dependencies

- `pydantic`: For data validation and settings management
- `sqlite3`: For response caching
- OpenAI API credentials:
  - API key (required)
  - Organization ID (optional)

### Basic Usage Example

```python
from src.llm.openai import OpenAI
from src.llm.core import TextChat, TextUserMessage

# Initialize the OpenAI implementation
llm = OpenAI(
    model="gpt-3.5-turbo",
    api_key="your-api-key",
    org_id=None  # Optional
)

# Create a chat
chat = TextChat(
    messages=[TextUserMessage(content="Hello, how are you?")],
    system_prompt="You are a helpful assistant."  # Optional
)

# Get a single prediction
response = llm.predict(chat)

# Get multiple samples
samples = llm.sample(chat, num_samples=3, temperature=0.7)

# Check usage costs
total_cost = llm.total_cost()
```

## Design Patterns

The interface implements several design patterns:
- **Abstract Base Class**: For defining the interface contract
- **Builder Pattern**: For constructing API requests
- **Factory Pattern**: For message creation
- **Strategy Pattern**: For different LLM implementations

## Error Handling

The interface includes proper error handling for:
- Invalid message sequences
- API failures (with retries)
- Unsupported model configurations
- Cache operation failures

## Best Practices

1. Always initialize the LLM with proper credentials
2. Use system prompts to set context when needed
3. Consider using caching for development and testing
4. Monitor costs using the `total_cost()` method
5. Handle potential API errors in your implementation

## Future Extensibility

The interface is designed to be extensible:
- New LLM providers can be added by implementing `BaseLLM`
- Additional features can be added to the base class
- Cache implementation can be modified or replaced
- Cost calculation can be updated for new models
