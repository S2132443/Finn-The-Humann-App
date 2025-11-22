FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=app
ENV FLASK_ENV=development

# Expose port
EXPOSE 5000

# Run the application
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
