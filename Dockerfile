# Use an official Python runtime as a parent image
FROM python:3.11-bookworm

# Set the working directory to /app
WORKDIR /app

# Install deps
COPY pyproject.toml ./
RUN pip install .[dev]
RUN pip install .[tests]

# Install the entire app
COPY . /app
RUN pip install -e .
