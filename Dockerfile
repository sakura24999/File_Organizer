FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for tkinter and other libraries
RUN apt-get update && apt-get install -y \
    python3-tk \
    libx11-6 \
    libfontconfig1 \
    libfreetype6 \
    libxrender1 \
    libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
COPY src ./src
COPY setup.py .
COPY README.md .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

# Command to run the application
CMD ["python", "-m", "src.main"]