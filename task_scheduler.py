import mysql.connector
import time
import random
import sys
import uuid
import datetime
from dateutil.relativedelta import relativedelta

db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': '3307',
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS database")
conn.commit()

db_config['database'] = 'database'
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

def execute_task(task_id, scheduled_time):
    print(f"Executing task with ID {task_id} at scheduled time {scheduled_time}...")
    time.sleep(random.randint(1, 5))
    print(f"Task with ID {task_id} completed.")

def check_and_execute_tasks():
    current_time = int(time.time())
    query = "SELECT id, name, scheduled_time, recurrence FROM tasks WHERE scheduled_time <= %s"
    cursor.execute(query, (current_time,))
    tasks = cursor.fetchall()
    for task in tasks:
        task_id, name, scheduled_time, recurrence = task
        execute_task(task_id, scheduled_time)
        if recurrence:
            if recurrence == 'daily':
                update_task(task_id, name, scheduled_time + 86400, 'daily')  # Increment by 24 hours
            elif recurrence == 'weekly':
                update_task(task_id, name, scheduled_time + 604800, 'weekly')  # Increment by 7 days
            elif recurrence == 'monthly':
                next_month = datetime.datetime.fromtimestamp(scheduled_time) + relativedelta(months=1)
                update_task(task_id, name, int(next_month.timestamp()), 'monthly')
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
        scheduled_time = int(sys.argv[3])
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
            print(task)
        
    elif command == "update":
        if len(sys.argv) != 5 and len(sys.argv) != 6:
            print("Usage: python task_scheduler.py update <task_id> <new_name> <new_scheduled_time> [recurrence]")
            sys.exit(1)
        task_id = sys.argv[2]
        new_name = sys.argv[3]
        new_scheduled_time = int(sys.argv[4])
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
