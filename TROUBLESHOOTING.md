# Troubleshooting Guide for Soularr Dashboard

## Common Issues and Solutions

### Failure Detection
- Automatically detects two types of import failures:
   - Initial failures: `Failed to import from: /mnt/Plex11/slskd/complete/[album]`
   - Move confirmations: `Failed import moved to: failed_imports/[album]`
   - Logs failures with timestamps to failure_list.txt
   - Displays failures in dedicated dashboard window

### Scheduled Operation
- Can be configured to run during off-peak hours (1 AM - 6 AM)
- Uses cron for scheduling:
   - Start: 0 1 * * * cd /home/eric/Soularr && docker compose up -d
   - Stop: 0 6 * * * cd /home/eric/Soularr && docker compose down
- State and progress preserved between sessions

### Log File Access Problems
1. Error: "No such file or directory: '/data/soularr.log'"
   Solution:
   - Verify soularr.log exists
   - Check permissions: chmod 644 /data/soularr.log
   - Ensure docker-compose.yml has correct volume mappings

2. Error: "Permission denied: '/data/failure_list.txt'"
   Solution:
   - Check file ownership: chown root:root /data/failure_list.txt
   - Set correct permissions: chmod 644 /data/failure_list.txt

3. Error: "Empty or missing failure list"
   Solution:
   - Verify failure_list.txt exists: touch /home/<user>/Soularr/failure_list.txt
   - Check permissions: chmod 644 /home/<user>/Soularr/failure_list.txt
   - Ensure docker-compose.yml has correct volume mapping for /data


### Docker Container Issues
1. Error: "Container soularr-dashboard not starting"
   Solution:
   - Check logs: docker logs soularr-dashboard
   - Verify port 8080 is not in use: netstat -tuln | grep 8080
   - Restart container: docker compose restart dashboard

2. Error: "Unable to find group docker"
   Solution:
   - Add current user to docker group: usermod -aG docker <user>
   - Restart Docker service: systemctl restart docker

### Web Interface Problems
1. Error: "Cannot connect to dashboard"
   Solution:
   - Verify container is running: docker ps
   - Check container logs: docker logs soularr-dashboard
   - Ensure port 8080 is accessible
   - Try accessing via localhost: http://localhost:8080

2. Error: "Logs not updating"
   Solution:
   - Check browser console for JavaScript errors
   - Verify log files are being written to
   - Restart the dashboard container

### Display Issues
1. Problem: "Log windows not equal size"
   Solution:
   - Clear browser cache
   - Try different browser
   - Check screen resolution (minimum 1024x768 recommended)

2. Problem: "Text overflow in log windows"
   Solution:
   - Horizontal scrolling is enabled by default
   - Adjust window size in index.html if needed

## Quick Commands Reference
- View dashboard logs:
  docker logs -f soularr-dashboard

- Restart dashboard:
  docker compose restart dashboard

- Check log file permissions:
  ls -l /data/soularr.log /data/failure_list.txt

- View running containers:
  docker ps | grep soularr

## Still Having Issues?
1. Check all file permissions and ownership
2. Verify all required files are in correct locations
3. Ensure Docker and Docker Compose are up to date
4. Check system resources (CPU, memory, disk space)
