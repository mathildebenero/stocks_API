# Use Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements and source code
COPY requirements.txt .
COPY main.py .
COPY routes.py .

# Install dependencies
# can be "RUN pip install -r requirements.txt" but "--no-cache-dir" makes the build process lighter.
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5001
EXPOSE 5001

# Run the Flask app
CMD ["python", "main.py"]
