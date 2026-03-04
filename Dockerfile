FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the internal port
EXPOSE 5000

# Ensure there are no dashes before the brackets
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]