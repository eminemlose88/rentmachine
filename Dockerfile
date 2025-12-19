# Unified Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Make run script executable
RUN chmod +x run.sh

# Expose port (Streamlit)
EXPOSE 8080

# Command to run both
CMD ["./run.sh"]
