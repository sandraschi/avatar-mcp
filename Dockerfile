FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    git \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install VRM/GLTF dependencies
RUN pip install --no-cache-dir numpy pygltflib

# Install remaining requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a directory for VRM models
RUN mkdir -p /app/models

# Expose the MCP server port (default: 8000)
EXPOSE 8000

# Expose metrics port (default: 8001)
EXPOSE 8001

# Set the default command to run the MCP server
CMD ["python", "-m", "avatarmcp.server", "--host", "0.0.0.0"]
