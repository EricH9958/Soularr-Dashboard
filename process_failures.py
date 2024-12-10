import time
import re
from datetime import datetime

def parse_logs_continuously(input_file, output_file):
    with open(input_file, 'r') as infile:
        infile.seek(0, 2)  # Move to end of file
        while True:
            line = infile.readline()
            if not line:
                time.sleep(1)
                continue
                
            # Check both failure patterns
            import_match = re.search(r'Failed to import from: .+/complete/(.+)', line)
            move_match = re.search(r'Failed import moved to: failed_imports/(.+)', line)
            
            if import_match or move_match:
                # Only log the first occurrence of a failure
                if import_match:
                    album_name = import_match.group(1)
                    current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    failure_entry = f"{current_time} - {album_name}, Failed Import\n"
                    with open(output_file, 'a') as outfile:
                        outfile.write(failure_entry)

if __name__ == '__main__':
    parse_logs_continuously('/data/soularr.log', '/data/failure_list.txt')
