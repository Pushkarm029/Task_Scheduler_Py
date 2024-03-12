import mysql.connector
import time
import random
import sys
import os
import uuid
import datetime
from dateutil.relativedelta import relativedelta

def get_db_config():
    if os.environ.get('CLUSTER_ENV') == 'k8s':
        return {
            'user': os.environ.get('MARIADB_USER', 'root'),
            'password': os.environ.get('MARIADB_PASSWORD', 'root'),
            'host': os.environ.get('MARIADB_HOST', 'my-release-mariadb.default.svc.cluster.local'),
            'port': os.environ.get('MARIADB_PORT', '3306'),
        }
    else:
        return {
            'user': 'root',
            'password': 'root',
            'host': 'localhost',
            'port': '3306',
        }

db_config= get_db_config()
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

database_name = os.environ.get('DATABASE_NAME', 'localdb1')

cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(database_name))
conn.commit()

db_config['database'] = database_name
conn.close()
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    scheduled_time BIGINT NOT NULL,
    recurrence VARCHAR(20) DEFAULT NULL
);
"""

cursor.execute(SCHEMA)
conn.commit()

def create_task(name, scheduled_time, recurrence=None):
    task_id = str(uuid.uuid4())
    query = "INSERT INTO tasks (id, name, scheduled_time, recurrence) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (task_id, name, scheduled_time, recurrence))
    conn.commit()

def read_tasks():
    query = "SELECT * FROM tasks"
    cursor.execute(query)
    return cursor.fetchall()

def update_task(task_id, name, scheduled_time, recurrence=None):
    query = "UPDATE tasks SET name = %s, scheduled_time = %s, recurrence = %s WHERE id = %s"
    cursor.execute(query, (name, scheduled_time, recurrence, task_id))
    conn.commit()

def delete_task(task_id):
    query = "DELETE FROM tasks WHERE id = %s"
    cursor.execute(query, (task_id,))
    conn.commit()

def execute_task(task_id, name, scheduled_time):
    print(f"Executing task {name} at scheduled time {datetime.datetime.fromtimestamp(scheduled_time)}...")
    time.sleep(random.randint(1, 5))
    print(f"Task with ID {task_id} completed.")

def check_and_execute_tasks():
    current_time = int(time.time())
    query = "SELECT id, name, scheduled_time, recurrence FROM tasks WHERE scheduled_time <= %s"
    cursor.execute(query, (current_time,))
    tasks = cursor.fetchall()
    for task in tasks:
        task_id, name, scheduled_time, recurrence = task
        execute_task(task_id, name, scheduled_time)
        if recurrence:
            if recurrence == 'daily':
                update_task(task_id, name, scheduled_time + 86400, 'daily')
            elif recurrence == 'weekly':
                update_task(task_id, name, scheduled_time + 604800, 'weekly')
            elif recurrence == 'monthly':
                next_month = int((datetime.datetime.fromtimestamp(scheduled_time) + relativedelta(months=1)).timestamp())
                update_task(task_id, name, next_month, 'monthly')
        else:
            delete_task(task_id)
    time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python task_scheduler.py <command>")
        print("Available commands: create, read, update, delete")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) != 4 and len(sys.argv) != 5:
            print("Usage: python task_scheduler.py create <name> <scheduled_time> [recurrence]")
            sys.exit(1)
        name = sys.argv[2]
        scheduled_time = int(datetime.datetime.strptime(sys.argv[3], '%Y-%m-%d %H:%M:%S').timestamp())
        recurrence = sys.argv[4] if len(sys.argv) == 5 else None
        create_task(name, scheduled_time, recurrence)
        print("Task created successfully.")
        print("Executing Tasks..")
        check_and_execute_tasks()
        
    elif command == "read":
        print("Executing Tasks..")
        check_and_execute_tasks()
        tasks = read_tasks()
        print("Tasks:")
        for task in tasks:
            id, name, scheduled_time, recurrence = task
            scheduled_time = datetime.datetime.fromtimestamp(scheduled_time)
            task = f"ID: {id}, Name: {name}, Scheduled Time: {scheduled_time}, Recurrence: {recurrence}"
            print(task)
        
    elif command == "update":
        if len(sys.argv) != 5 and len(sys.argv) != 6:
            print("Usage: python task_scheduler.py update <task_id> <new_name> <new_scheduled_time> [recurrence]")
            sys.exit(1)
        task_id = sys.argv[2]
        new_name = sys.argv[3]
        new_scheduled_time = int(datetime.datetime.strptime(sys.argv[4], '%Y-%m-%d %H:%M:%S').timestamp())
        recurrence = sys.argv[5] if len(sys.argv) == 6 else None
        update_task(task_id, new_name, new_scheduled_time, recurrence)
        print("Task updated successfully.")
        print("Executing Tasks..")
        check_and_execute_tasks()
  
    elif command == "delete":
        if len(sys.argv) != 3:
            print("Usage: python task_scheduler.py delete <task_id>")
            sys.exit(1)
        task_id = sys.argv[2]
        delete_task(task_id)
        print("Task deleted successfully.")
        print("Executing Tasks..")
        check_and_execute_tasks()
        
    else:
        print("Invalid command. Available commands: create, read, update, delete")
