# Use the official Python image as the base image
FROM python:3.13-rc-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the Python scripts and requirements.txt into the container
COPY task_scheduler.py /app/
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the Python script when the container launches
CMD ["python", "task_scheduler.py"]
