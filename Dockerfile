FROM python:3.11-slim

# Install MPI
RUN apt-get update && apt-get install -y \
    mpich \
    libmpich-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "web_server.py"]
