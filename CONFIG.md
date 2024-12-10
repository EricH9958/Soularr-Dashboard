# Configuration Guide for Soularr Dashboard

## Security Configuration

### Credential Management
- config.ini: Contains private configuration (not tracked in git)
- config.ini.example: Template with masked credentials
- Required settings:
  api_key = YOUR_API_KEY_HERE
  private_token = YOUR_TOKEN_HERE

## Docker Configuration Options

### Environment Variables
- PUID=1000               # User ID for permissions
- PGID=1000               # Group ID for permissions
- TZ=America/Los_Angeles  # Your timezone

### Volume Mappings
- /home/<user>/Soularr/dashboard:/app  # Dashboard application files
- /home/<user>/Soularr:/data          # Data directory for logs
- /var/run/docker.sock:/var/run/docker.sock  # Docker socket for container communication

## Dashboard Customization

### Log Display
- Number of log lines displayed: 100 (modify in dashboard.py)
- Auto-refresh interval: 1 second (modify in index.html)
- Log order: Newest first (reverse chronological)
- Failure detection: Real-time monitoring
- Failure list: Separate window display

### Scheduled Operation
- Default run time: 1 AM - 6 AM
- Cron configuration:
  0 1 * * * cd /home/eric/Soularr && docker compose up -d
  0 6 * * * cd /home/eric/Soularr && docker compose down

### Visual Customization
Modify these values in templates/index.html:

Window Heights:
- Log window height: 600px
- Font size: 12px
- Line height: 1.4

Colors:
- Background: #f0f0f0
- Log window: #000 (black)
- Log text: #0f0 (green)
- Headers: #333 (dark gray)

## Port Configuration
Default port: 8080 (modify in Dockerfile and dashboard.py if needed)
