# Use an official lightweight Python image.
FROM python:3.10-slim-bullseye

# 配置 apt 使用国内源
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list

# 配置 pip 使用国内源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Set the working directory in the container
WORKDIR /app

# Install python venv
RUN apt-get update && apt-get install -y python3-venv && rm -rf /var/lib/apt/lists/*

# Install uv globally in the container
RUN pip install uv

# Copy only the dependency file first to leverage Docker cache
COPY pyproject.toml ./

# Create a virtual environment and install dependencies
# This layer is cached as long as pyproject.toml doesn't change
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --no-cache-dir --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    requests \
    python-dotenv \
    mysql-connector-python \
    fastapi \
    uvicorn[standard] \
    pydantic \
    click \
    typing-extensions


# Now copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8001

# Use the python from the venv to run uvicorn as a module
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]