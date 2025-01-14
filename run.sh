#!/usr/bin/env bash

# Requires agent code and test set to be present locally:
# - candidate/agent.py
# - test_set/test_questions.json, etc.

# Run docker build
docker build -t ml-evaluator .

touch results.json

# Run the container, mounting candidate and secret test sets as read-only volumes.
docker run --rm \
    -v "$(pwd)/candidate":/candidate:ro \
    -v "$(pwd)/test_set":/test_set:ro \
    -v "$(pwd)/results.json:/app/results.json:rw" \
    ml-evaluator
