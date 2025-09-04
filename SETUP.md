# 📋 Complete Setup Guide

This guide will walk you through setting up your own instance of the Cloudflare Tunnel for Options Data project.

## 🎯 What You'll Build

A secure, public API endpoint like: `https://api.yourdomain.com/ticker/ETH/5SEP25`

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Python 3.8+** installed (`python3 --version`)
- [ ] **Git** installed (`git --version`)
- [ ] **Cloudflare account** with a domain
- [ ] **Redis database** with options data
- [ ] **Terminal/Command line** access

## 🚀 Step-by-Step Setup

### Step 1: Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/yourusername/cloudflare-tunnel.git
cd cloudflare-tunnel

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Install Cloudflare CLI

**macOS:**
```bash
brew install cloudflare/cloudflare/cloudflared
```

**Linux:**
```bash
# Ubuntu/Debian
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# CentOS/RHEL
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.rpm
sudo rpm -i cloudflared-linux-amd64.rpm
```

**Verify Installation:**
```bash
cloudflared --version
```

### Step 3: Configure Environment

Create `.env` file in project directory:

```bash
cat > .env << EOF
# Redis connection settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API settings  
API_PORT=8002

# Cloudflare tunnel name (choose unique name)
TUNNEL_NAME=my-options-tunnel
EOF
```

**Adjust Redis settings** to match your setup:
- If Redis is on different host: change `REDIS_HOST`
- If using different port: change `REDIS_PORT` 
- If using different database: change `REDIS_DB`

### Step 4: Set Up Cloudflare Tunnel

#### 4.1 Login to Cloudflare
```bash
cloudflared tunnel login
```
This opens a browser window. Login to your Cloudflare account and authorize.

#### 4.2 Create Tunnel
```bash
# Replace 'my-options-tunnel' with your chosen tunnel name
cloudflared tunnel create my-options-tunnel
```

**Important:** Copy the tunnel ID from the output (looks like: `a1b2c3d4-e5f6-7890-1234-567890abcdef`)

#### 4.3 Update Configuration

Edit `config.yml` and replace placeholders:

```yaml
# Replace YOUR_TUNNEL_ID with actual tunnel ID
tunnel: a1b2c3d4-e5f6-7890-1234-567890abcdef
credentials-file: /Users/YOURUSERNAME/.cloudflared/a1b2c3d4-e5f6-7890-1234-567890abcdef.json

ingress:
  # Replace with your actual domain
  - hostname: api.yourdomain.com
    service: http://localhost:8002
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      tlsTimeout: 10s
      httpHostHeader: localhost:8002
  
  # Required catch-all rule
  - service: http_status:404
```

**Update paths:**
- Replace `YOURUSERNAME` with your actual username
- Replace `yourdomain.com` with your actual domain

#### 4.4 Create DNS Route
```bash
# Replace with your tunnel name and domain
cloudflared tunnel route dns my-options-tunnel api.yourdomain.com
```

### Step 5: Configure Data Access

Edit `allowed_tickers.json` to specify which data to expose:

```json
{
  "allowed": [
    {
      "asset": "ETH",
      "expiry": "5SEP25"
    },
    {
      "asset": "BTC",
      "expiry": "5SEP25"  
    },
    {
      "asset": "ETH",
      "expiry": "26DEC25"
    }
  ]
}
```

**Important:** Only ticker/expiry combinations in this file will be accessible via the API.

### Step 6: Test Setup

#### 6.1 Test Local API
```bash
# Start API server only
python tunnel_api.py
```

In another terminal:
```bash
# Test health endpoint
curl http://localhost:8002/health

# Test ticker endpoint (should return data or empty if no data)
curl http://localhost:8002/ticker/ETH/5SEP25
```

Stop the API server (Ctrl+C) before proceeding.

#### 6.2 Start Complete Setup
```bash
# This starts both API server and tunnel
./start.sh
```

### Step 7: Verify Public Access

Wait 1-2 minutes for tunnel to establish, then test:

```bash
# Test your public endpoint
curl https://api.yourdomain.com/health
curl https://api.yourdomain.com/ticker/ETH/5SEP25
```

Or visit in browser: `https://api.yourdomain.com/`

## ✅ Success Checklist

Your setup is working if:

- [ ] Local API responds: `curl http://localhost:8002/health` returns JSON
- [ ] Public API responds: `curl https://api.yourdomain.com/health` returns JSON
- [ ] Ticker data accessible: `https://api.yourdomain.com/ticker/ETH/5SEP25` shows options data
- [ ] Non-allowed tickers return 404: `https://api.yourdomain.com/ticker/INVALID/INVALID`

## 🔧 Configuration Options

### Adding More Data

To expose more ticker/expiry combinations:

1. Edit `allowed_tickers.json`
2. Add new entries to the "allowed" array
3. Changes take effect immediately (no restart needed)

### Changing Domain

To use a different domain:

1. Update `config.yml` hostname
2. Create new DNS route: `cloudflared tunnel route dns my-options-tunnel new.domain.com`
3. Restart tunnel

### Changing Port

To use a different local port:

1. Update `.env` file: `API_PORT=8003`
2. Update `config.yml` service: `http://localhost:8003`
3. Restart both services

## 🚨 Common Issues & Solutions

### Issue: "Port already in use"
```bash
# Find and kill process using port
lsof -ti:8002
kill -9 <PID>
```

### Issue: "Tunnel connection failed"
```bash
# Check tunnel status
cloudflared tunnel info my-options-tunnel

# Re-authenticate if needed
cloudflared tunnel login
```

### Issue: "DNS not resolving"
- Wait up to 24 hours for DNS propagation
- Check Cloudflare DNS settings in dashboard
- Verify tunnel route: `cloudflared tunnel route dns list`

### Issue: "Empty data response"
- Verify expiry date format (no leading zeros: `5SEP25` not `05SEP25`)
- Check if data exists in Redis: `redis-cli KEYS "option:ETH-5SEP25*"`
- Ensure ticker is in `allowed_tickers.json`

### Issue: "Redis connection failed"
- Check Redis is running: `redis-cli ping`
- Verify connection details in `.env` file
- Check firewall/network connectivity

## 🔍 Debug Commands

```bash
# Test Redis connection
python -c "from external_db_access import test_connection; print(test_connection())"

# List available Redis keys
redis-cli KEYS "option:*" | head -20

# Check tunnel status
cloudflared tunnel list

# View tunnel logs
cloudflared tunnel --config config.yml run

# Test local API
curl -v http://localhost:8002/health
```

## 📱 Managing Your Setup

### Starting Services
```bash
./start.sh
```

### Stopping Services
Press `Ctrl+C` in the terminal where `start.sh` is running

### Viewing Logs
- API logs: Visible in terminal where `start.sh` runs
- Tunnel logs: Also visible in same terminal

### Updating Data
- Edit `allowed_tickers.json` - changes are immediate
- Restart not required for configuration changes

## 🌐 Going Live

### Domain Setup
1. Ensure domain is managed by Cloudflare
2. DNS should automatically be configured by tunnel setup
3. SSL certificate is automatically provided by Cloudflare

### Security Considerations
- Only whitelisted data is exposed
- API doesn't expose Redis directly
- All traffic is HTTPS encrypted
- Cloudflare provides DDoS protection

### Monitoring
- Health endpoint: `https://api.yourdomain.com/health`
- Configuration: `https://api.yourdomain.com/config`
- Tunnel status: `cloudflared tunnel info my-options-tunnel`

## 🤝 Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Review debug commands above
3. Check project documentation
4. Open an issue on GitHub repository

## 🎉 Congratulations!

You now have a secure, public API serving your options data via Cloudflare Tunnel!

**Your API is available at:** `https://api.yourdomain.com`

**Next steps:**
- Share your API endpoints with users
- Monitor usage and performance
- Add more ticker/expiry combinations as needed
- Consider setting up monitoring/alerting