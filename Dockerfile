# Use an official lightweight Python image.
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install uv globally in the container
RUN pip install uv

# Copy only the dependency file first to leverage Docker cache
COPY pyproject.toml ./

# Create a virtual environment and install dependencies
# This layer is cached as long as pyproject.toml doesn't change
RUN uv venv && \
    . .venv/bin/activate && \
    uv sync

# Now copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8010

# Use the python from the venv to run uvicorn as a module
CMD ["/bin/bash", "-c", "source /app/.venv/bin/activate && python -m uvicorn api.main:app --host 0.0.0.0 --port 8010 --reload"]