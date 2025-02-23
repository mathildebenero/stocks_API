# Use Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
COPY main.py .
COPY routes.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5002
EXPOSE 5002

# Run the Flask app
CMD ["python", "main.py"]
