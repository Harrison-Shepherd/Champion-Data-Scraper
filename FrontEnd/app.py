import json
import os
import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template_string, request, jsonify
import subprocess  # Used to call external Python scripts
import threading
import time

app = Flask(__name__)

# Initialize log messages list
log_messages = []

# Initialize scraping status
scraping_status = {"status": "idle", "progress": 0}

def connect():
    """Establish and return a connection to the MySQL database using mysql-connector."""
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',  # Change as needed
            port=3306,          # Change as needed
            user='root',        # Change as needed
            password='powerdata',  # Change as needed
            database='PowerData'  # Change as needed
        )
        if connection.is_connected():
            log("Successfully connected to the MySQL database 'PowerData'.")
            return connection
    except Error as e:
        log(f"Error connecting to the MySQL database: {e}")
        return None

def log(message):
    """Log messages to the log_messages list."""
    log_messages.append(message)

def select_database(connection, db_name):
    """Select the database before executing any SQL commands."""
    try:
        cursor = connection.cursor()
        cursor.execute(f"USE `{db_name}`;")
        log(f"Database selected: {db_name}")
    except Exception as e:
        log(f"Error selecting database: {e}")

@app.route('/create_database', methods=['POST'])
def create_database():
    """Endpoint to create a new database."""
    db_name = request.form.get('db_name')
    if db_name:
        connection = connect()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(f"CREATE DATABASE `{db_name}`;")
                log(f"Database '{db_name}' created successfully.")
                cursor.close()
            except Error as e:
                log(f"Error creating database '{db_name}': {e}")
            finally:
                connection.close()
    return render_template_string(template(), logs=log_messages)

@app.route('/delete_database', methods=['POST'])
def delete_database():
    """Endpoint to delete an existing database."""
    db_name = request.form.get('db_name')
    if db_name:
        connection = connect()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(f"DROP DATABASE `{db_name}`;")
                log(f"Database '{db_name}' deleted successfully.")
                cursor.close()
            except Error as e:
                log(f"Error deleting database '{db_name}': {e}")
            finally:
                connection.close()
    return render_template_string(template(), logs=log_messages)

def scrape_entire_database():
    """Scrape the entire database and update scraping progress."""
    scraping_status["status"] = "in_progress"
    scraping_status["progress"] = 0

    try:
        result = subprocess.run(['python', 'main.py'], capture_output=True, text=True)
        log(f"Scrape output: {result.stdout}")
        if result.stderr:
            log(f"Scrape error: {result.stderr}")
    except Exception as e:
        log(f"Error during scraping: {e}")
    finally:
        scraping_status["status"] = "complete"
        scraping_status["progress"] = 100

def start_scraping_thread():
    """Start scraping in a new thread to allow progress tracking."""
    scraping_thread = threading.Thread(target=scrape_entire_database)
    scraping_thread.start()
    for i in range(1, 101):
        scraping_status["progress"] = i
        time.sleep(0.1)  # Simulate progress

@app.route('/scrape_database', methods=['POST'])
def scrape_database():
    start_scraping_thread()
    return render_template_string(template(), logs=log_messages)

@app.route('/scraping_status')
def get_scraping_status():
    """Endpoint to get the scraping progress."""
    return jsonify(scraping_status)

@app.route('/')
def home():
    """Home route to render the main HTML interface and log messages."""
    return render_template_string(template(), logs=log_messages)

def template():
    """HTML template with CSS for styling, including a progress bar."""
    return """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Database Manager</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f4;
                color: #333;
                padding: 20px;
            }
            h1 {
                color: #C00000;
                font-size: 24px;
                text-align: center;
                margin-bottom: 5px;
            }
            .banner {
                text-align: center;
                padding: 10px;
                color: #666;
                margin-bottom: 20px;
            }
            .container {
                max-width: 700px;
                margin: auto;
                background: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }
            .button-group {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }
            input[type="text"] {
                padding: 8px;
                width: calc(100% - 100px);
                margin-right: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            .btn {
                padding: 10px;
                color: white;
                border: none;
                cursor: pointer;
                border-radius: 4px;
                width: 100%;
            }
            .btn-create { background-color: #28a745; }
            .btn-delete { background-color: #dc3545; }
            .btn-scrape { background-color: #007bff; }
            .btn:hover { opacity: 0.9; }
            .logs {
                background: #fff;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                max-height: 300px;
                overflow-y: auto;
                margin-top: 20px;
            }
            .log-message { margin: 5px 0; padding: 5px; border-left: 5px solid #C00000; }
            .progress-bar {
                width: 100%;
                background-color: #f3f3f3;
                border-radius: 5px;
                margin-top: 20px;
            }
            .progress-bar-fill {
                height: 20px;
                width: 0;
                background-color: #C00000;
                border-radius: 5px;
                text-align: center;
                color: white;
                line-height: 20px;
            }
            footer {
                text-align: center;
                margin-top: 20px;
                color: #888;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Database Manager</h1>
            <div class="banner">
                <p>Welcome to the Database Manager. Here you can create and delete databases, scrape data, and monitor logs.</p>
            </div>
            <form method="POST" action="/create_database" class="button-group">
                <input type="text" name="db_name" placeholder="Enter Database Name" required>
                <button type="submit" class="btn btn-create">Create Database</button>
            </form>
            <form method="POST" action="/delete_database" class="button-group">
                <input type="text" name="db_name" placeholder="Enter Database Name" required>
                <button type="submit" class="btn btn-delete">Delete Database</button>
            </form>
            <form method="POST" action="/scrape_database" class="button-group">
                <button type="submit" class="btn btn-scrape">Scrape Entire Database</button>
            </form>
            <div class="progress-bar">
                <div class="progress-bar-fill" id="progress-bar-fill">0%</div>
            </div>
            <div class="logs">
                <h2>Log Messages:</h2>
                {% for log in logs %}
                    <div class="log-message">{{ log }}</div>
                {% endfor %}
            </div>
        </div>
        <footer>
            Powered by Flask • Database Management Tool
        </footer>
        <script>
            function updateProgress() {
                fetch('/scraping_status')
                    .then(response => response.json())
                    .then(data => {
                        const progressBarFill = document.getElementById('progress-bar-fill');
                        progressBarFill.style.width = data.progress + '%';
                        progressBarFill.innerHTML = data.progress + '%';

                        if (data.status === 'in_progress') {
                            setTimeout(updateProgress, 100);
                        }
                    });
            }
            updateProgress();
        </script>
    </body>
    </html>
    """
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

