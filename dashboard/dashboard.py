from flask import Flask, render_template
from flask_socketio import SocketIO
import json
import subprocess
import time
import re
from datetime import datetime
import threading

app = Flask(__name__)
socketio = SocketIO(app)

def monitor_logs():
    try:
        with open('/data/soularr.log', 'r') as log_file:
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
                    with open('/data/failure_list.txt', 'a') as outfile:
                        outfile.write(failure_entry)
    except Exception as e:
        print(f"Error in monitor_logs: {str(e)}")


def get_docker_logs():
    try:
        with open('/data/soularr.log', 'r') as f:
            logs = f.readlines()
            return logs[-50:][::-1]
    except Exception as e:
        return [f"Error accessing logs: {str(e)}"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs')
def get_logs():
    try:
        docker_logs = get_docker_logs()
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
    # Start the log monitoring thread
    monitor_thread = threading.Thread(target=monitor_logs, daemon=True)
    monitor_thread.start()
    
    # Run the Flask-SocketIO app
    socketio.run(app, host='0.0.0.0', port=8080,
debug=False, allow_unsafe_werkzeug=True)    
