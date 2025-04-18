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
# LOG_PATH = '/home/eric/soularr/logs/soularr.log'
# FAILURE_PATH = '/home/eric/soularr/failure_list.txt'

LOG_PATH = os.environ.get('LOG_PATH', '/logs/soularr.log')
FAILURE_PATH = os.environ.get('FAILURE_PATH', '/data/failure_list.txt')


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
                port=8082, 
                debug=False, 
                allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main()

