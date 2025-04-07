onfiguration Guide for Soularr Dashboard

## Directory Structure
/home/<user>/Soularr/
├── data/
│   └── logs/
│       └── soularr.log
├── dashboard/
│   ├── templates/
│   ├── dashboard.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── config.ini

## Logging Configuration

### config.ini Settings
[Logging]
level = INFO
format = [%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s
datefmt = %Y-%m-%dT%H:%M:%S%z
filename = /data/logs/soularr.log

### Log Levels Available
- DEBUG: Detailed information for debugging
- INFO: General operational information
- WARNING: Warning messages for potential issues
- ERROR: Error messages for serious problems
- CRITICAL: Critical errors that may prevent operation

### Docker Log Rotation
Configured in docker-compose.yml:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

## Docker Configuration

### Dashboard Service Settings
- Port: 8080 (default)
- Network Mode: host
- User Permissions: PUID=1000, PGID=1000
- Timezone: Configurable via TZ environment variable
- Volume Mappings:
  - /home/<user>/Soularr/dashboard:/app
  - /home/<user>/Soularr:/data
  - /home/<user>/Soularr/data/logs:/data/logs

### Environment Variables
- PUID: User ID (default: 1000)
- PGID: Group ID (default: 1000)
- TZ: Timezone (example: America/Los_Angeles)

## Dashboard Settings

### Web Interface
- Default URL: http://your-server-ip:8080
- Auto-refresh interval: 1 second
- Log display: 50 most recent entries
- Window split: 50/50 for logs and failures

### Failure Tracking
- Location: /data/failure_list.txt
- Format: [Date Time] - [Artist/Album], Failed Import
- Auto-updates when failures occur

## Security Considerations
- Default network mode is 'host'
- No authentication required (internal network use recommended)
- Log files are readable by user:group 1000:1000
- Docker socket mounted read-only

## Maintenance
- Logs automatically rotate at 10MB
- Keeps last 3 log files
- Failed imports list grows indefinitely (manual cleanup may be needed)
- Docker images should be updated regularly

## Troubleshooting
- Check log file permissions
- Verify directory structure exists
- Ensure Docker has proper access rights
- Monitor disk space for log storage

