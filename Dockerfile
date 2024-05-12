# Based on the official Python 3.12 image
FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install required packages
# RUN apt-get update && apt-get install -y libpq-dev gcc

# Install dds_glossary package
RUN pip install .
