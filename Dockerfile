# Use Python 3.12 slim variant to match pyproject.toml requirements
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy the pyproject.toml and source to leverage the project standards
COPY pyproject.toml .
COPY . .

# Extract dependencies from pyproject.toml and write to requirements.txt
RUN python -c "import tomllib; open('requirements.txt', 'w').write('\n'.join(tomllib.load(open('pyproject.toml', 'rb'))['project']['dependencies']))"

# Install dependencies into the local environment
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /code

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY ./app /code/app

# Create a non-root user and switch to it for security
RUN addgroup --system app && \
    adduser --system --group app && \
    chown -R app:app /code
USER app

# Expose the port the app runs on
EXPOSE 8080

# Add healthcheck using built-in python to avoid installing curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Use uvicorn for production deployment
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]