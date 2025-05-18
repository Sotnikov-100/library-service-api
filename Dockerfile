# Use the official Python 3.13 Alpine image as the base image
FROM python:3.13-alpine

# Set the maintainer's contact information
LABEL maintainer="Library"

# Set environment variables
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache gcc musl-dev linux-headers

# Set the working directory inside the container
WORKDIR /app

# Copy dependency files into the container
COPY requirements.txt ./

# Install dependencies, sync with uv requirements.txt, and clean up unnecessary files
RUN pip install --no-cache-dir uv &&\
    uv pip install --system --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache /root/.pip

# Copy the rest of the application code into the container
COPY . .

# Create necessary directories, set permissions, and make entrypoint executable
RUN adduser --disabled-password --home /home/django-user django-user && \
    mkdir -p /files/media /files/static && \
    chown -R django-user:django-user /files /home/django-user && \
    chmod -R 755 /files /home/django-user


EXPOSE 8000

# Switch to the non-root user
USER django-user
