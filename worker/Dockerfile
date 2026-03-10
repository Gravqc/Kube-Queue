FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy source code
COPY src/ ./src/

# Install project
RUN poetry install --no-interaction --no-ansi

# Run worker with unbuffered output
CMD ["python", "-u", "-m", "kubequeue_worker.worker"]
