# Troubleshooting Guide

Common issues and solutions for the Cloudflare Tunnel Options API.

## 🔧 Quick Diagnostics

Run these commands to quickly diagnose issues:

```bash
# Check if API is running locally
curl -s http://localhost:8001/health | jq '.status'

# Check Redis connection
python -c "from external_db_access import test_connection; print('✅ Connected' if test_connection() else '❌ Failed')"

# Check configuration
cat allowed_tickers.json | jq '.allowed | length'

# Check if Docker containers are running
docker ps | grep bybit
```

## 🚨 Common Issues

### 1. API Won't Start

#### Symptoms
- `./start.sh` fails to start
- Port 8001 already in use
- Import errors

#### Solutions

**Port Already in Use:**
```bash
# Find what's using port 8001
lsof -i :8001

# Kill the process
kill $(lsof -t -i:8001)

# Or use different port
export API_PORT=8002
./start.sh
```

**Missing Dependencies:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or create fresh virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Import Errors:**
```bash
# Check if files exist
ls -la external_db_access.py db_config.py

# Check Python path
python -c "import external_db_access; print('✅ OK')"
```

### 2. Database Connection Failed

#### Symptoms
- Health check shows `"database": "disconnected"`
- 503 errors when accessing ticker endpoints
- "Database connection failed" messages

#### Solutions

**Check if options-data-b is running:**
```bash
# Check Docker containers
docker ps | grep bybit

# If not running, start it
cd /Users/anujsainicse/claude/options-data-b
./docker-start.sh
```

**Check Redis port mapping:**
```bash
# Verify Redis port
docker port bybit-redis

# Should show: 6379/tcp -> 0.0.0.0:6380
```

**Test connection directly:**
```bash
# Test Redis connection
redis-cli -h localhost -p 6380 ping

# Should return: PONG
```

**Fix configuration:**
```bash
# Check .env file
cat .env | grep REDIS

# Should show:
# REDIS_HOST=localhost
# REDIS_PORT=6380
# REDIS_DB=0
```

### 3. Cloudflare Tunnel Issues

#### Symptoms
- Tunnel won't start
- DNS not resolving
- 502 Bad Gateway errors

#### Solutions

**Tunnel Creation Issues:**
```bash
# Check if cloudflared is installed
cloudflared --version

# Check if authenticated
ls ~/.cloudflared/cert.pem

# If not, re-authenticate
cloudflared tunnel login
```

**Tunnel ID Problems:**
```bash
# List existing tunnels
cloudflared tunnel list

# Check config.yml has correct tunnel ID
grep "tunnel:" config.yml

# Update with correct ID if needed
```

**DNS Resolution:**
```bash
# Check DNS record
nslookup ticker.yourdomain.com

# If not found, recreate
cloudflared tunnel route dns options-ticker ticker.yourdomain.com

# Wait 5-10 minutes for DNS propagation
```

**502 Bad Gateway:**
```bash
# Check if API is running locally
curl http://localhost:8001/health

# Check tunnel config service URL
grep "service:" config.yml

# Should be: service: http://localhost:8001
```

### 4. Configuration Issues

#### Symptoms
- `404` errors for valid tickers
- `"configuration": "empty"` in health check
- JSON parsing errors

#### Solutions

**Invalid JSON:**
```bash
# Validate JSON
cat allowed_tickers.json | jq empty

# If error, fix JSON format
```

**Missing Configuration:**
```bash
# Check if file exists
ls -la allowed_tickers.json

# Check format
cat allowed_tickers.json
```

**Case Sensitivity:**
```bash
# Assets must be uppercase
# Expiry format must match exactly
# Example: "29DEC23" not "29dec23" or "29-DEC-23"
```

### 5. Empty Data Issues

#### Symptoms
- API returns `"options": []`
- Zero options in summary
- Valid ticker combinations but no data

#### Solutions

**Check if data exists in main database:**
```bash
# Connect to main API
curl http://localhost:8000/api/assets/BTC

# Check specific expiry
curl http://localhost:8000/api/expiries/BTC
```

**Verify ticker format:**
```bash
# List all available symbols
curl http://localhost:8000/api/symbols?asset=BTC | jq '.symbols[0:5]'

# Check expiry format matches
```

**Database sync issues:**
```bash
# Restart options tracker
cd /Users/anujsainicse/claude/options-data-b
docker restart bybit-tracker
```

## 🔍 Advanced Debugging

### Enable Debug Logging

**API Debug Mode:**
```bash
# Start with debug logging
export LOG_LEVEL=DEBUG
python tunnel_api.py
```

**Cloudflare Debug Mode:**
```bash
# Start tunnel with debug logs
cloudflared tunnel --config config.yml --loglevel debug run
```

### Network Debugging

**Check Local Connectivity:**
```bash
# Test local API
curl -v http://localhost:8001/health

# Test with different IPs
curl -v http://127.0.0.1:8001/health
curl -v http://0.0.0.0:8001/health
```

**Check External Connectivity:**
```bash
# Test from external network
curl -v https://ticker.yourdomain.com/health

# Test with different DNS
nslookup ticker.yourdomain.com 8.8.8.8
```

### Performance Debugging

**Check Response Times:**
```bash
# Time API responses
time curl -s http://localhost:8001/health

# Time database queries
time curl -s http://localhost:8001/ticker/BTC/29DEC23
```

**Monitor Resource Usage:**
```bash
# Check API process
ps aux | grep tunnel_api

# Check memory usage
top -p $(pgrep -f tunnel_api)
```

## 📊 Health Monitoring

### Continuous Health Checks

**Simple Monitor:**
```bash
#!/bin/bash
# monitor.sh
while true; do
    if curl -s http://localhost:8001/health | jq -e '.status == "healthy"' > /dev/null; then
        echo "$(date): ✅ Healthy"
    else
        echo "$(date): ❌ Unhealthy"
    fi
    sleep 30
done
```

**Detailed Monitor:**
```python
import requests
import time
import json
from datetime import datetime

def detailed_health_check():
    try:
        # Check local API
        local_resp = requests.get('http://localhost:8001/health', timeout=10)
        local_healthy = local_resp.status_code == 200
        
        # Check public API (if configured)
        try:
            public_resp = requests.get('https://ticker.yourdomain.com/health', timeout=10)
            public_healthy = public_resp.status_code == 200
        except:
            public_healthy = False
        
        # Check database stats
        if local_healthy:
            data = local_resp.json()
            db_connected = data.get('database') == 'connected'
            config_loaded = data.get('configuration') == 'loaded'
            
            return {
                'timestamp': datetime.now().isoformat(),
                'local_api': local_healthy,
                'public_api': public_healthy,
                'database': db_connected,
                'configuration': config_loaded,
                'available_tickers': data.get('available_tickers', 0)
            }
        else:
            return {
                'timestamp': datetime.now().isoformat(),
                'local_api': False,
                'public_api': public_healthy,
                'database': False,
                'configuration': False,
                'available_tickers': 0
            }
            
    except Exception as e:
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'local_api': False,
            'public_api': False,
            'database': False,
            'configuration': False
        }

# Run every minute
while True:
    status = detailed_health_check()
    print(json.dumps(status, indent=2))
    time.sleep(60)
```

## 🛠️ Recovery Procedures

### Complete Restart

**Full System Restart:**
```bash
# 1. Stop everything
pkill -f tunnel_api.py
pkill -f cloudflared

# 2. Restart Docker containers
cd /Users/anujsainicse/claude/options-data-b
docker restart bybit-redis bybit-tracker bybit-dataapi

# 3. Wait for containers
sleep 30

# 4. Test Redis connection
python -c "from external_db_access import test_connection; print(test_connection())"

# 5. Restart tunnel API
cd /Users/anujsainicse/claude/cloudflare-tunnel
./start.sh
```

### Configuration Reset

**Reset to Default Configuration:**
```bash
# Backup current config
cp allowed_tickers.json allowed_tickers.json.backup

# Create minimal config
cat > allowed_tickers.json << EOF
{
  "allowed": [
    {"asset": "BTC", "expiry": "29DEC23"}
  ]
}
EOF

# Test with minimal config
curl http://localhost:8001/config
```

### Emergency Procedures

**If Public API is Down:**
```bash
# 1. Check if it's a local issue
curl http://localhost:8001/health

# 2. If local is OK, restart tunnel
pkill -f cloudflared
cloudflared tunnel --config config.yml run &

# 3. If local is down, full restart
./start.sh
```

**If Database is Corrupted:**
```bash
# 1. Check main system
cd /Users/anujsainicse/claude/options-data-b
docker logs bybit-tracker | tail -20

# 2. Restart tracker if needed
docker restart bybit-tracker

# 3. Wait for data collection
sleep 60

# 4. Test tunnel API
curl http://localhost:8001/health
```

## 📝 Log Analysis

### Important Log Patterns

**API Logs:**
```bash
# Success patterns
grep "GET /health" tunnel.log | tail -5

# Error patterns  
grep "ERROR" tunnel.log
grep "500" tunnel.log
grep "Database connection failed" tunnel.log
```

**Cloudflare Logs:**
```bash
# Connection issues
grep "connection refused" tunnel.log
grep "502" tunnel.log

# DNS issues
grep "no such host" tunnel.log
```

### Log Collection

**Collect All Logs:**
```bash
#!/bin/bash
# collect_logs.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="logs_$TIMESTAMP"
mkdir -p $LOG_DIR

# API logs (if running)
ps aux | grep tunnel_api > $LOG_DIR/processes.txt

# Docker logs
docker logs bybit-redis --tail 100 > $LOG_DIR/redis.log 2>&1
docker logs bybit-tracker --tail 100 > $LOG_DIR/tracker.log 2>&1
docker logs bybit-dataapi --tail 100 > $LOG_DIR/dataapi.log 2>&1

# Configuration
cp allowed_tickers.json $LOG_DIR/
cp config.yml $LOG_DIR/
cp .env $LOG_DIR/

# System info
curl -s http://localhost:8001/health > $LOG_DIR/health.json 2>&1
curl -s http://localhost:8001/config > $LOG_DIR/config.json 2>&1

echo "Logs collected in: $LOG_DIR"
```

## 📞 Getting Help

### Information to Collect

When asking for help, provide:

1. **System Information:**
   ```bash
   uname -a
   python --version
   docker --version
   cloudflared --version
   ```

2. **Error Messages:**
   ```bash
   # Recent logs
   tail -50 tunnel.log
   ```

3. **Configuration:**
   ```bash
   # Sanitized config (remove sensitive data)
   cat allowed_tickers.json
   head -10 config.yml
   ```

4. **Health Status:**
   ```bash
   curl -s http://localhost:8001/health | jq
   ```

### Support Checklist

- [ ] Tried basic restart: `./start.sh`
- [ ] Verified Docker containers running
- [ ] Tested Redis connection
- [ ] Checked configuration JSON validity
- [ ] Verified Cloudflare tunnel status
- [ ] Collected relevant logs
- [ ] Documented exact error messages
- [ ] Listed steps to reproduce issue

---

**Still having issues?** Check the detailed setup guide in [CLOUD.md](CLOUD.md) or the API documentation in [README.md](README.md).