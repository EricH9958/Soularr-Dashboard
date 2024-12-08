# /home/eric/Soularr/dashboard/dashboard.py
from flask import Flask, render_template
import json
import subprocess

app = Flask(__name__)

def get_docker_logs():
    try:
        # Read from soularr log file
        with open('/data/soularr.log', 'r') as f:
            logs = f.readlines()
            # Get last 50 lines
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

