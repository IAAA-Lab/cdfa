# Use lightweight Python slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching (add your deps)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY app.py .
COPY *.ttl .
COPY *.rdf .

# Expose port
EXPOSE 5013

# Run the application
CMD ["python", "app.py"]
