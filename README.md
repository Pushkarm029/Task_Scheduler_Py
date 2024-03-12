# Task-Scheduler.Py
This Python script provides a simple task scheduling service using MariaDB as the backend database. It allows users to create, read, update, and delete tasks with optional recurrence settings.:

## Features
- Task Management: Create, read, update, and delete tasks.
- Recurrence Support: Tasks can be set to recur daily, weekly, or monthly.
- Execution: Automatically executes tasks at their scheduled times.

## Tech Stack
- Python
- Helm
- Kubernetes
- Docker

## How to run?

### Locally (Challenge 1 (Programming))
```bash
# install all required dependencies
pip install --no-cache-dir -r requirements.txt

# Start mariadb container
docker compose up

# Create Task
python task_scheduler.py create <name> <scheduled_time> [recurrence]

# Example
python task_scheduler.py create "Task Name" "2024-03-13 10:00:00" daily

# Read Tasks
python task_scheduler.py read

# Delete Task
python task_scheduler.py delete <task_id>

# Example
python task_scheduler.py delete '0a9c0a93-f8df-43d5-8b00-e0340bc78e65'

# Update Task
python task_scheduler.py update <task_id> <new_name> <new_scheduled_time> [recurrence]

# Example
python task_scheduler.py update '2cadf6af-a941-4321-98cb-7d4aac68e54d' pm "2024-03-13 10:00:00" monthly
```

### K8s Environment (Challenge 2 (Helm))
```bash
# Start k8s cluster locally
minikube start

# Deploy MariaDB HELM chart
helm install my-release oci://registry-1.docker.io/bitnamicharts/mariadb

# wait for MariaDB to start
kubectl get pods -w --namespace default -l app.kubernetes.io/instance=my-release

# password setup
chmod +x update-passwords.sh # give permission to script file

./setpass.sh # run script to set password

# Create Task
helm install -f ./createjob/values.yaml createjob ./createjob --set taskName=example-task,scheduledTime="2024-03-13 10:00:00",recurrence=daily

# Read Task
helm install -f ./readjob/values.yaml readjob ./readjob

# Delete Task
helm install -f ./deletejob/values.yaml deletejob ./deletejob --set taskId=2cadf6af-a941

# Update Task
helm install -f ./updatejob/values.yaml updatejob ./updatejob --set taskId=2cadf6af-a941,newName=example-task2,newScheduledTime="2024-03-13 10:00:00",newRecurrence=daily
```

### Build Docker Image
```bash
docker build -t pushkarm029/my-task-scheduler .
```

## How It Works
### Task Creation:

- Users can create tasks by providing a name, scheduled time, and optional recurrence setting (daily, weekly, monthly).
- Tasks are stored in a MySQL database with a unique identifier (id), name, scheduled time, and recurrence information.

### Task Execution: 
- The service continuously checks for tasks scheduled to be executed.
- Upon reaching their scheduled time, tasks are automatically executed.
- Execution involves a simulated delay of random duration (1 to 5 seconds) to mimic task processing.

### Recurrence Handling:

- Recurring tasks are automatically updated with their next scheduled time after execution.
- Daily tasks increment their scheduled time by 24 hours.
- Weekly tasks increment their scheduled time by 7 days.
- Monthly tasks move to the next month's equivalent date.

### User Interaction:

Users can interact with the service through command-line commands (create, read, update, delete).
These commands allow users to manage tasks effectively, including viewing, updating, and deleting tasks.

### Environment Configuration:

- The service can adapt to different environments by reading environment variables for database connection settings.
- In a Kubernetes environment, it dynamically fetches database connection details from environment variables (CLUSTER_ENV, MARIADB_USER, MARIADB_PASSWORD, MARIADB_HOST, MARIADB_PORT).

### Charts Configuration:
Created 4 different helm charts 
- createjob
- deletejob
- readjob
- updatejob

This service offers a simple yet effective solution for task scheduling, ensuring timely execution and easy management of tasks with minimal user intervention.
