FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the internal port
EXPOSE 5000

# Start Gunicorn (App variable inside app.py)
CMD ["python", "run.py"]