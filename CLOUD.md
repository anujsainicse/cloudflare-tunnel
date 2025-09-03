# Cloudflare Tunnel Setup Guide

Complete step-by-step guide to set up Cloudflare Tunnel for your options data API.

## 📋 Prerequisites

- Cloudflare account
- Domain managed by Cloudflare
- macOS/Linux terminal
- Your options-data-b system running

## 🚀 Step-by-Step Setup

### Step 1: Install Cloudflare Tunnel

```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Verify installation
cloudflared --version
```

### Step 2: Authenticate with Cloudflare

```bash
# This opens browser for authentication
cloudflared tunnel login
```

After authentication, you'll see:
```
You have successfully logged in.
If you wish to copy your credentials to a server, they have been saved to:
/Users/anujsainicse/.cloudflared/cert.pem
```

### Step 3: Create Your Tunnel

```bash
# Create tunnel (replace 'options-ticker' with your preferred name)
cloudflared tunnel create options-ticker
```

You'll get output like:
```
Tunnel credentials written to /Users/anujsainicse/.cloudflared/12345678-1234-1234-1234-123456789abc.json
Created tunnel options-ticker with id 12345678-1234-1234-1234-123456789abc
```

**⚠️ Important**: Copy the tunnel ID (12345678-1234-1234-1234-123456789abc)

### Step 4: Update Configuration

Edit `config.yml` in your cloudflare-tunnel directory:

```yaml
# Replace [TUNNEL_ID] with your actual tunnel ID
tunnel: 12345678-1234-1234-1234-123456789abc
credentials-file: /Users/anujsainicse/.cloudflared/12345678-1234-1234-1234-123456789abc.json

ingress:
  # Replace ticker.yourdomain.com with your actual domain
  - hostname: ticker.yourdomain.com
    service: http://localhost:8001
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      tlsTimeout: 10s
      httpHostHeader: localhost:8001
  
  # Catch-all rule (required)
  - service: http_status:404
```

### Step 5: Create DNS Record

```bash
# Replace with your tunnel name and desired subdomain
cloudflared tunnel route dns options-ticker ticker.yourdomain.com
```

You'll see:
```
Added CNAME ticker.yourdomain.com which will route to tunnel 12345678-1234-1234-1234-123456789abc
```

### Step 6: Configure Your API

Edit `allowed_tickers.json` to specify which data should be public:

```json
{
  "allowed": [
    {
      "asset": "BTC",
      "expiry": "29DEC23"
    },
    {
      "asset": "ETH",
      "expiry": "29DEC23"
    }
  ]
}
```

### Step 7: Test Locally First

```bash
cd /Users/anujsainicse/claude/cloudflare-tunnel/
python tunnel_api.py
```

Test endpoints:
```bash
# In another terminal
curl http://localhost:8001/
curl http://localhost:8001/health
curl http://localhost:8001/config
curl http://localhost:8001/ticker/BTC/29DEC23
```

### Step 8: Start the Tunnel

```bash
# Stop the local test first (Ctrl+C)
# Then start with the tunnel
./start.sh
```

You should see:
```
🚀 Starting Options Ticker Tunnel...
✅ API server started successfully
🌩️  Starting Cloudflare tunnel...
✅ System started successfully!
📊 Local API: http://localhost:8001
🌐 Public URL: Check your Cloudflare dashboard
```

### Step 9: Test Public Access

```bash
# Test your public URL (replace with your domain)
curl https://ticker.yourdomain.com/
curl https://ticker.yourdomain.com/health
curl https://ticker.yourdomain.com/ticker/BTC/29DEC23
```

## 🔧 Configuration Examples

### Basic Configuration

**For BTC and ETH options on Dec 29, 2023:**

```json
{
  "allowed": [
    {"asset": "BTC", "expiry": "29DEC23"},
    {"asset": "ETH", "expiry": "29DEC23"}
  ]
}
```

**Public URLs:**
- ✅ `https://ticker.yourdomain.com/ticker/BTC/29DEC23`
- ✅ `https://ticker.yourdomain.com/ticker/ETH/29DEC23`
- ❌ `https://ticker.yourdomain.com/ticker/SOL/29DEC23` (404)

### Multiple Expiry Dates

```json
{
  "allowed": [
    {"asset": "BTC", "expiry": "29DEC23"},
    {"asset": "BTC", "expiry": "5JAN24"},
    {"asset": "BTC", "expiry": "12JAN24"},
    {"asset": "ETH", "expiry": "29DEC23"},
    {"asset": "ETH", "expiry": "5JAN24"}
  ]
}
```

### All Assets for Specific Date

```json
{
  "allowed": [
    {"asset": "BTC", "expiry": "29DEC23"},
    {"asset": "ETH", "expiry": "29DEC23"},
    {"asset": "SOL", "expiry": "29DEC23"}
  ]
}
```

## 🌐 Cloudflare Dashboard

### Tunnel Status

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Select your account and domain
3. Go to **Zero Trust** → **Networks** → **Tunnels**
4. You should see your tunnel with status **Healthy**

### DNS Records

1. Go to **DNS** → **Records**
2. You should see a CNAME record:
   - **Name**: ticker
   - **Content**: 12345678-1234-1234-1234-123456789abc.cfargotunnel.com
   - **Status**: Proxied (orange cloud)

### Traffic Analytics

1. Go to **Analytics & Logs** → **Web Traffic**
2. Filter by your subdomain to see tunnel traffic

## 🛡️ Security Features

### Built-in Protections

- **DDoS Protection**: Cloudflare automatically protects against attacks
- **HTTPS**: All traffic is encrypted (SSL/TLS)
- **Rate Limiting**: Can be configured in Cloudflare dashboard
- **Geo Blocking**: Block traffic from specific countries (optional)
- **Bot Protection**: Filter automated traffic (optional)

### Access Policies (Optional)

You can add access restrictions in Cloudflare Zero Trust:

1. Go to **Zero Trust** → **Access** → **Applications**
2. Add application: `ticker.yourdomain.com`
3. Create policies (IP restrictions, email domains, etc.)

## 📊 Monitoring & Logs

### Tunnel Health Monitoring

```bash
# Check tunnel status
cloudflared tunnel info options-ticker

# View tunnel list
cloudflared tunnel list
```

### API Health Monitoring

```bash
# Health check
curl https://ticker.yourdomain.com/health

# Response should be:
{
  "status": "healthy",
  "database": "connected",
  "configuration": "loaded",
  "available_tickers": 2,
  "timestamp": "2023-12-20T15:30:00.123456"
}
```

### Log Files

**Local API Logs**: Console output when running tunnel_api.py
**Tunnel Logs**: Console output when running cloudflared

**Optional**: Configure file logging in config.yml:

```yaml
tunnel: your-tunnel-id
credentials-file: /path/to/credentials.json

log:
  level: info
  file: /Users/anujsainicse/.cloudflared/tunnel.log

ingress:
  - hostname: ticker.yourdomain.com
    service: http://localhost:8001
  - service: http_status:404
```

## 🔄 Management Commands

### Start/Stop Services

```bash
# Start everything
./start.sh

# Stop (Ctrl+C or):
pkill -f "tunnel_api.py"
pkill -f "cloudflared"
```

### Update Configuration

```bash
# Edit ticker configuration
nano allowed_tickers.json

# Changes take effect immediately (no restart needed)
```

### Tunnel Management

```bash
# List tunnels
cloudflared tunnel list

# Delete tunnel (if needed)
cloudflared tunnel delete options-ticker

# Recreate tunnel
cloudflared tunnel create options-ticker
```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. Tunnel Won't Start

**Error**: `tunnel with name options-ticker already exists`

**Solution**:
```bash
# List existing tunnels
cloudflared tunnel list

# Use existing tunnel ID in config.yml
# OR delete and recreate:
cloudflared tunnel delete options-ticker
cloudflared tunnel create options-ticker
```

#### 2. DNS Not Resolving

**Error**: `ticker.yourdomain.com` not found

**Solutions**:
```bash
# Check DNS record exists
nslookup ticker.yourdomain.com

# Recreate DNS record
cloudflared tunnel route dns options-ticker ticker.yourdomain.com

# Wait 5-10 minutes for DNS propagation
```

#### 3. API Connection Failed

**Error**: `Database connection failed`

**Solutions**:
```bash
# Check if options-data-b is running
docker ps | grep bybit

# Test Redis connection
python -c "from external_db_access import test_connection; print(test_connection())"

# Start options-data-b if needed
cd /Users/anujsainicse/claude/options-data-b
./docker-start.sh
```

#### 4. 502 Bad Gateway

**Error**: Cloudflare shows 502 error

**Solutions**:
```bash
# Check if API is running locally
curl http://localhost:8001/health

# Check tunnel configuration
grep -A 5 "ingress:" config.yml

# Restart API
pkill -f tunnel_api.py
python tunnel_api.py &
```

#### 5. 404 for Valid Ticker

**Error**: `ticker/date combination BTC/29DEC23 is not available`

**Solutions**:
```bash
# Check configuration
cat allowed_tickers.json

# Verify exact format (case-sensitive)
curl https://ticker.yourdomain.com/config

# Check if data exists in database
curl http://localhost:8001/ticker/BTC/29DEC23
```

### Debug Commands

```bash
# Test local API
curl -v http://localhost:8001/health

# Test tunnel connectivity
cloudflared tunnel --config config.yml run --url http://localhost:8001

# Check tunnel logs
cloudflared tunnel --config config.yml --loglevel debug run

# Test DNS resolution
dig ticker.yourdomain.com
nslookup ticker.yourdomain.com
```

## 🔒 Security Recommendations

### 1. Regular Updates

```bash
# Update cloudflared
brew upgrade cloudflared

# Update Python dependencies
pip install -U fastapi uvicorn redis python-dotenv
```

### 2. Monitor Access

- Check Cloudflare analytics regularly
- Set up alerts for unusual traffic patterns
- Review which ticker combinations are being accessed

### 3. Configuration Management

- Keep `allowed_tickers.json` minimal
- Remove old/unused ticker combinations
- Document why each combination is exposed

### 4. Backup Configuration

```bash
# Backup important files
cp config.yml config.yml.backup
cp allowed_tickers.json allowed_tickers.json.backup
cp ~/.cloudflared/*.json ~/cloudflared-backup/
```

## 📈 Performance Optimization

### 1. API Response Caching

Add caching to tunnel_api.py (optional):

```python
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def get_cached_ticker_data(asset: str, expiry: str, cache_time: int):
    # cache_time changes every 60 seconds, invalidating cache
    db = connect_to_database()
    return db.get_options_by_expiry(expiry, asset)

@app.get("/ticker/{asset}/{expiry}")
async def get_ticker(asset: str, expiry: str):
    cache_time = int(time.time() // 60)  # 1-minute cache
    options = get_cached_ticker_data(asset, expiry, cache_time)
    # ... rest of function
```

### 2. Cloudflare Caching

Configure caching rules in Cloudflare dashboard:

1. Go to **Caching** → **Page Rules**
2. Add rule: `ticker.yourdomain.com/ticker/*`
3. Set **Cache Level**: Cache Everything
4. Set **Edge Cache TTL**: 1 minute

### 3. Rate Limiting

Configure in Cloudflare dashboard:

1. Go to **Security** → **WAF**
2. Add rate limiting rule
3. Example: 100 requests per minute per IP

## 🎯 Production Checklist

- [ ] Tunnel created and configured
- [ ] DNS record pointing to tunnel
- [ ] API responding to health checks
- [ ] Only required ticker combinations configured
- [ ] HTTPS working correctly
- [ ] Monitoring/alerting set up
- [ ] Documentation updated
- [ ] Team notified of public endpoints
- [ ] Backup of configuration files
- [ ] Regular update schedule planned

## 📞 Support Resources

- **Cloudflare Docs**: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- **Tunnel Troubleshooting**: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/troubleshooting/
- **Community Forum**: https://community.cloudflare.com/