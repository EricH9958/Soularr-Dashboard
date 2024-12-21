# Troubleshooting Guide for Soularr Dashboard

## Common Issues and Solutions

### Logs Not Appearing in Dashboard

1. Check Log File Location
- Verify /home/<user>/Soularr/data/logs exists
- Ensure soularr.log is present
- Check permissions:
ls -l /home/<user>/Soularr/data/logs/soularr.log
- Should show: -rw-r--r-- 1 1000 1000

2. Check Docker Volume Mounts
- Verify in docker-compose.yml:
  - /home/<user>/Soularr:/data
  - /home/<user>/Soularr/data/logs:/data/logs
- Run: docker compose config
- Check container can access logs:
docker exec soularr-dashboard ls -l /data/logs/soularr.log

3. Check Log Configuration
- Verify config.ini has correct path:
filename = /data/logs/soularr.log
- Ensure log level is set correctly:
level = INFO

### Dashboard Not Loading

1. Check Container Status
docker compose ps
docker logs soularr-dashboard

2. Check Port Access
- Verify port 8080 is available:
netstat -tuln | grep 8080
- Test local access:
curl http://localhost:8080

3. Check Network Mode
- Verify 'network_mode: host' in docker-compose.yml
- Restart container if needed:
docker compose restart dashboard

### Log Rotation Issues

1. Check Docker Logging Config
- Verify logging settings in docker-compose.yml:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

2. Monitor Log Size
ls -lh /home/<user>/Soularr/data/logs/
du -h /home/<user>/Soularr/data/logs/soularr.log

3. Manual Log Cleanup (if needed)
cd /home/<user>/Soularr/data/logs/
mv soularr.log soularr.log.old
touch soularr.log
chmod 644 soularr.log
docker compose restart

### Permission Issues

1. Check File Ownership
ls -l /home/<user>/Soularr/data/logs/
sudo chown -R 1000:1000 /home/<user>/Soularr/data/logs/

2. Check Directory Permissions
chmod 755 /home/<user>/Soularr/data/logs
chmod 644 /home/<user>/Soularr/data/logs/soularr.log

3. Verify Docker User Settings
- Check PUID and PGID in docker-compose.yml
- Should match your user:
id <user>

### Container Communication Issues

1. Check Network Settings
docker network ls
docker compose ps

2. Verify Host Network Mode
- Both containers should use:
network_mode: host

3. Check Container Logs
docker logs soularr
docker logs soularr-dashboard

### Dashboard Display Issues

1. Check Web Browser Console
- Open browser developer tools (F12)
- Look for errors in console

2. Verify WebSocket Connection
- Check browser network tab
- Look for socket.io connections

3. Test Dashboard Access
curl http://localhost:8080
curl http://your-server-ip:8080

### Quick Reset Procedure

If all else fails:
1. Stop containers:
docker compose down

2. Clear logs:
cd /home/<user>/Soularr/data/logs/
rm soularr.log*
touch soularr.log
chmod 644 soularr.log

3. Reset permissions:
sudo chown -R 1000:1000 /home/<user>/Soularr/data/logs/

4. Restart containers:
docker compose up -d

5. Monitor logs:
docker logs -f soularr-dashboard

