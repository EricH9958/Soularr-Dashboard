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

def monitor_logs():
    # Create failure_list.txt if it doesn't exist
    if not os.path.exists('/data/failure_list.txt'):
        open('/data/failure_list.txt', 'w').close()

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
                    failure_entry = f"

