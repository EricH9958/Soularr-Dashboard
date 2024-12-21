Installation Guide for Soularr Dashboard

## Directory Setup
1. Create the required directory structure:

mkdir -p /home/<user>/Soularr/dashboard/templates
mkdir -p /home/<user>/Soularr/data/logs
chmod 755 /home/<user>/Soularr/data/logs

### Directory Structure

/home/<user>/Soularr/
├── data/
│   └── logs/
└── dashboard/
    └── templates/

## Required Files

1. Create dashboard.py in /home/<user>/Soularr/dashboard/:

from flask import Flask, render_template
from flask_socketio import SocketIO
import json
import subprocess
import time
import re
from datetime import datetime
import threading
import os

app = Flask(__name__)
socketio = SocketIO(app)

# Define constant paths
LOG_PATH = '/data/logs/soularr.log'
FAILURE_PATH = '/data/failure_list.txt'

def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(FAILURE_PATH), exist_ok=True)

def monitor_logs():
    ensure_directories()

    # Create failure_list.txt if it doesn't exist
    if not os.path.exists(FAILURE_PATH):
        open(FAILURE_PATH, 'w').close()

    while True:
        try:
            with open(LOG_PATH, 'r') as log_file:
                log_file.seek(0, 2)  # Move to end of file
                while True:
                    line = log_file.readline()
                    if not line:
                        time.sleep(1)
                        continue

                    # Emit log update to dashboard
                    socketio.emit('log_update', {'data': line})

                    # Check for both types of failures
                    import_match = re.search(r'Failed to import from: .+/complete/(.+)', line)
                    move_match = re.search(r'Failed import moved to: failed_imports/(.+)', line)
                    
                    if import_match or move_match:
                        artist_name = import_match.group(1) if import_match else move_match.group(1)
                        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                        failure_entry = f"{current_time} - {artist_name}, Failed Import\n"
                        
                        with open(FAILURE_PATH, 'a+') as f:
                            f.seek(0)
                            if failure_entry not in f.readlines():
                                f.write(failure_entry)

        except FileNotFoundError:
            print(f"Waiting for log file to be created: {LOG_PATH}")
            time.sleep(5)
        except Exception as e:
            print(f"Error in monitor_logs: {str(e)}")
            time.sleep(5)

def get_docker_logs():
    """Retrieve the last 50 lines of logs"""
    try:
        with open(LOG_PATH, 'r') as f:
            logs = f.readlines()
            return logs[-50:][::-1]  # Return last 50 lines in reverse order
    except FileNotFoundError:
        return ["Log file not found. Waiting for logs to be generated..."]
    except Exception as e:
        return [f"Error accessing logs: {str(e)}"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs')
def get_logs():
    try:
        docker_logs = get_docker_logs()
        
        try:
            with open(FAILURE_PATH, 'r') as f:
                failure_logs = f.readlines()
        except FileNotFoundError:
            open(FAILURE_PATH, 'w').close()
            failure_logs = []
        except Exception as e:
            failure_logs = [f"Error reading failure logs: {str(e)}"]

        return json.dumps({
            'docker_logs': docker_logs,
            'failure_logs': failure_logs
        })
    except Exception as e:
        return json.dumps({
            'docker_logs': [f"Error accessing logs: {str(e)}"],
            'failure_logs': []
        })

def main():
    ensure_directories()
    
    # Start the log monitoring thread
    monitor_thread = threading.Thread(target=monitor_logs, daemon=True)
    monitor_thread.start()

    # Run the Flask-SocketIO app
    socketio.run(app, 
                host='0.0.0.0', 
                port=8080, 
                debug=False, 
                allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main()

2. Create requirements.txt in /home/<user>/Soularr/dashboard/:

flask==3.0.0
flask-socketio==5.3.6
python-socketio==5.10.0
python-engineio==4.8.0
gunicorn==21.2.0
eventlet==0.33.3

3. Create Dockerfile in /home/<user>/Soularr/dashboard/:

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "dashboard.py"]

4. Create failure_list.txt in /home/<user>/Soularr/:

touch /home/<user>/Soularr/failure_list.txt
chmod 644 /home/<user>/Soularr/failure_list.txt

5. Configure logging in config.ini:

[Logging]
level = INFO
format = [%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s
datefmt = %Y-%m-%dT%H:%M:%S%z
filename = /data/logs/soularr.log

6. Create index.html in /home/<user>/Soularr/dashboard/templates/:

<!DOCTYPE html>
<html>
<head>
    <title>Soularr Log Monitor</title>
    <style>
        body {
            margin: 20px;
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
        }
        .container {
            display: flex;
            gap: 20px;
            margin-top: 20px;
            width: 100%;
        }
        .log-section {
            flex: 1;
            max-width: 50%;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .log-window {
            background: #000;
            color: #0f0;
            font-family: monospace;
            padding: 10px;
            height: 600px;
            overflow-y: auto;
            overflow-x: auto;
            white-space: pre;
            border-radius: 5px;
            font-size: 12px;
            line-height: 1.4;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }
        h2 {
            color: #333;
            margin: 0 0 10px 0;
            font-size: 18px;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
    <h1>Soularr Log Monitor</h1>
    <div class="container">
        <div class="log-section">
            <h2>Docker Logs</h2>
            <div id="docker-logs" class="log-window"></div>
        </div>
        <div class="log-section">
            <h2>Failure List</h2>
            <div id="failure-logs" class="log-window"></div>
        </div>
    </div>
    <script>
        const socket = io();

        function updateLogs() {
            fetch('/logs')
                .then(r => r.json())
                .then(data => {
                    if (data.docker_logs) {
                        document.getElementById('docker-logs').innerHTML =
                            data.docker_logs.join('\n');
                    }
                    if (data.failure_logs) {
                        document.getElementById('failure-logs').innerHTML =
                            data.failure_logs.join('');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }

        socket.on('log_update', function(data) {
            const dockerLogs = document.getElementById('docker-logs');
            dockerLogs.innerHTML = data.data + dockerLogs.innerHTML;
        });

        // Initial load
        updateLogs();

        // Refresh every second
        setInterval(updateLogs, 1000);
    </script>
</body>
</html>

7. Add to docker-compose.yml:

  dashboard:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    restart: unless-stopped
    container_name: soularr-dashboard
    network_mode: host
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/Los_Angeles
    volumes:
      - /home/<user>/Soularr/dashboard:/app
      - /home/<user>/Soularr:/data
      - /home/<user>/Soularr/data/logs:/data/logs
      - /var/run/docker.sock:/var/run/docker.sock
    working_dir: /app
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

8. Configure Scheduled Operation:
Create a cron job for the current user:

crontab -e

Add the following lines:

0 1 * * * cd /home/<user>/Soularr && docker compose up -d
0 6 * * * cd /home/<user>/Soularr && docker compose down

9. Build and Start:

docker compose down
docker compose build dashboard
docker compose up -d

10. Access:
Open your web browser and navigate to: http://your-server-ip:8080

