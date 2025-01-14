FROM python:3.10-slim

# Create app directory and set permissions first
RUN mkdir -p /app && \
    useradd -m evaluator && \
    chown -R evaluator:evaluator /app

WORKDIR /app

# Install any dependencies required for scoring
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Add the app directory to PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Copy over src and set permissions
COPY candidate/src /app/src
COPY candidate/.env /app/.env
COPY scoring_script.py /app/scoring_script.py
RUN chown -R evaluator:evaluator /app

# Switch to evaluator user
USER evaluator

# The entrypoint will be the scoring script.
ENTRYPOINT ["python", "scoring_script.py"]