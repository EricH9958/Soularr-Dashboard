# Installation Guide for Soularr Dashboard

## Directory Setup
1. Create the dashboard directory and templates folder:
mkdir -p /home/<user>/Soularr/dashboard/templates

## Required Files

1. Create dashboard.py in /home/<user>/Soularr/dashboard/:

from flask import Flask, render_template
import json
import subprocess

app = Flask(__name__)

def get_docker_logs():
    try:
        # Read from soularr log file
        with open('/data/soularr.log', 'r') as f:
            logs = f.readlines()
            # Get last 50 lines and reverse them
            return logs[-50:][::-1]
    except Exception as e:
        return [f"Error accessing logs: {str(e)}"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs')
def get_logs():
    try:
        # Get soularr logs
        docker_logs = get_docker_logs()
        
        # Get failure list
        with open('/data/failure_list.txt', 'r') as f:
            failure_logs = f.readlines()
        
        return json.dumps({
            'docker_logs': docker_logs,
            'failure_logs': failure_logs
        })
    except Exception as e:
        return json.dumps({
            'docker_logs': [f"Error accessing logs: {str(e)}"],
            'failure_logs': []
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

2. Create requirements.txt in /home/<user>/Soularr/dashboard/:

flask==3.0.0
gunicorn==21.2.0

3. Create Dockerfile in /home/<user>/Soularr/dashboard/:

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "dashboard:app"]

4. Create failure_list.txt in /home/<user>/Soularr/:

touch /home/<user>/Soularr/failure_list.txt
chmod 644 /home/<user>/Soularr/failure_list.txt




5. Create index.html in /home/<user>/Soularr/dashboard/templates/:

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
        
        // Initial load
        updateLogs();
        
        // Refresh every second
        setInterval(updateLogs, 1000);
    </script>
</body>
</html>

6. Add dashboard service to your docker-compose.yml:

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
    user: "root:root"
    volumes:
      - /home/<user>/Soularr/dashboard:/app
      - /home/<user>/Soularr:/data
      - /var/run/docker.sock:/var/run/docker.sock
    working_dir: /app

7. Build and Start:
docker compose down
docker compose build dashboard
docker compose up -d

8. Access:
Open your web browser and navigate to: http://your-server-ip:8080

