# Use the official Python image.
FROM python:3.9-slim

# Set the working directory.
WORKDIR /app

# Copy requirements and install them.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code.
COPY . .

# Expose the port on which the app will run.
ENV PORT 8080

# Use Gunicorn as the production server.
CMD exec gunicorn --config gunicorn.conf.py --graceful-timeout 300 --bind :$PORT webapp:app