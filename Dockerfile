# Use an official lightweight Python image.
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN pip install uv

# Copy the dependency definitions
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv pip sync pyproject.toml

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8010

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8010"]