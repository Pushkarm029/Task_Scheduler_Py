import mysql.connector.pooling
import time
import random
import sys
import uuid

# Database connection configuration
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': '3307',
    'database': 'tasks_db',
}

# Create a connection pool
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="pool",
                                                    pool_size=5,
                                                    **db_config)

# Function to create a new task
def create_task(name, scheduled_time):
    task_id = str(uuid.uuid4())
    query = "INSERT INTO tasks (id, name, scheduled_time) VALUES (%s, %s, %s)"
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute(query, (task_id, name, scheduled_time))
    conn.commit()
    cursor.close()
    conn.close()

# Function to read all tasks
def read_tasks():
    query = "SELECT * FROM tasks"
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return tasks

def update_task(task_id, name, scheduled_time):
    query = "UPDATE tasks SET name = %s, scheduled_time = %s WHERE id = %s"
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute(query, (name, scheduled_time, task_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_task(task_id):
    query = "DELETE FROM tasks WHERE id = %s"
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute(query, (task_id,))
    conn.commit()
    cursor.close()
    conn.close()

def execute_task(task_id, scheduled_time):
    print(f"Executing task with ID {task_id} at scheduled time {scheduled_time}...")
    time.sleep(random.randint(1, 5))
    print(f"Task with ID {task_id} completed.")

def check_and_execute_tasks():
    current_time = int(time.time())
    query = "SELECT id, name, scheduled_time FROM tasks WHERE scheduled_time <= %s"
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute(query, (current_time,))
    tasks = cursor.fetchall()
    for task in tasks:
        task_id, name, scheduled_time = task
        execute_task(task_id, scheduled_time)
        delete_task(task_id)
    cursor.close()
    conn.close()
    time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python task_scheduler.py <command>")
        print("Available commands: create, read, update, delete")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) != 4:
            print("Usage: python task_scheduler.py create <name> <scheduled_time>")
            sys.exit(1)
        name = sys.argv[2]
        scheduled_time = int(sys.argv[3])
        create_task(name, scheduled_time)
        print("Task created successfully.")
        check_and_execute_tasks()
        
    elif command == "read":
        tasks = read_tasks()
        print("Tasks:")
        for task in tasks:
            print(task)

        check_and_execute_tasks()
        
    elif command == "update":
        if len(sys.argv) != 5:
            print("Usage: python task_scheduler.py update <task_id> <new_name> <new_scheduled_time>")
            sys.exit(1)
        task_id = sys.argv[2]
        new_name = sys.argv[3]
        new_scheduled_time = int(sys.argv[4])
        update_task(task_id, new_name, new_scheduled_time)
        print("Task updated successfully.")
        check_and_execute_tasks()
        
    elif command == "delete":
        if len(sys.argv) != 3:
            print("Usage: python task_scheduler.py delete <task_id>")
            sys.exit(1)
        task_id = sys.argv[2]
        delete_task(task_id)
        print("Task deleted successfully.")
        check_and_execute_tasks()
        
    else:
        print("Invalid command. Available commands: create, read, update, delete")
