FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for building some python packages)
# RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock* /app/

# Install poetry and dependencies
# We export requirements to avoid installing poetry in the final image if we wanted to be strictly minimal,
# but for simplicity in this sprint, we'll just install via pip after generating requirements or just use pip directly if we had a requirements.txt.
# Since we have pyproject.toml, let's use poetry to export.
# ACTUALLY, to keep it simple and robust without relying on poetry being in the image:
# We will assume a `requirements.txt` is generated or we install poetry.
# Let's install poetry, it's easier to maintain dev/prod parity.

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

COPY . /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
