# Dockerfile
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# 1. Copy in and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy only your source code and main file
COPY src/ /app/src
COPY main.py /app/

# 3. Specify default command to run
CMD ["python", "main.py"]
