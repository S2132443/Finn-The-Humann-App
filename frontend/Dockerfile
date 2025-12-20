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

# Expose port (Railway will set PORT env var)
EXPOSE 5000

# Run the application with gunicorn for production
# Railway sets PORT environment variable, default to 5000 for local dev
CMD gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} 'app:create_app()'
