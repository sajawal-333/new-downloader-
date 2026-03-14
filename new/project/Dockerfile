# Use an official Python runtime as a parent image, based on Debian for full system library compatibility
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install required system dependencies (like FFmpeg)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Expose port (Cloud providers like Railway override this via ENV variable, but good practice for local)
EXPOSE 5000

# Run gunicorn server
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4
