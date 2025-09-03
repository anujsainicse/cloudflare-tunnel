# Cloudflare Tunnel for Options Data

This setup creates a public API tunnel that serves filtered options data from your Redis database. Only specific ticker/date combinations configured in `allowed_tickers.json` are accessible.

## 📁 Directory Structure

```
cloudflare-tunnel/
├── tunnel_api.py          # FastAPI server with filtered endpoints
├── db_config.py           # Redis connection configuration
├── external_db_access.py  # Database access module
├── allowed_tickers.json   # Configuration: which tickers/dates to expose
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── config.yml            # Cloudflare tunnel configuration
├── start.sh              # Startup script
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Configure Allowed Tickers

Edit `allowed_tickers.json` to specify which ticker/date combinations should be publicly accessible:

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
    },
    {
      "asset": "BTC",
      "expiry": "5JAN24"
    }
  ]
}
```

### 2. Test Locally

```bash
./start.sh
```

This will:
- Install dependencies
- Start the API server on http://localhost:8001
- Show configuration instructions for Cloudflare tunnel

### 3. Set Up Cloudflare Tunnel

```bash
# Install cloudflared
brew install cloudflare/cloudflare/cloudflared

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create options-ticker

# Note the tunnel ID and update config.yml
# Replace [TUNNEL_ID] with your actual tunnel ID

# Create DNS record
cloudflared tunnel route dns options-ticker ticker.yourdomain.com

# Start the tunnel
./start.sh
```

## 🌐 API Endpoints

### Available Endpoints

- `GET /` - API information and available combinations
- `GET /ticker/{asset}/{expiry}` - Get options data (if allowed)
- `GET /config` - Show current configuration
- `GET /health` - Health check

### Example Usage

```bash
# Get BTC options for Dec 29, 2023 (if configured)
curl https://ticker.yourdomain.com/ticker/BTC/29DEC23

# Check what's available
curl https://ticker.yourdomain.com/config

# Health check
curl https://ticker.yourdomain.com/health
```

### Response Format

```json
{
  "asset": "BTC",
  "expiry": "29DEC23",
  "timestamp": "2023-12-20T15:30:00.123456",
  "summary": {
    "total_options": 156,
    "call_options": 78,
    "put_options": 78,
    "total_volume_24h": 12500000.50,
    "total_open_interest": 8750000.25
  },
  "options": [
    {
      "symbol": "BTC-29DEC23-45000-C",
      "last_price": 1250.5,
      "mark_price": 1245.0,
      "volume_24h": 125000.0,
      "open_interest": 150.5,
      "delta": 0.65,
      "gamma": 0.0023,
      "theta": -12.5,
      "vega": 0.45,
      "mark_iv": 0.85,
      "underlying_price": 45123.45,
      "timestamp": 1703875200.0
    }
  ]
}
```

## ⚙️ Configuration

### Environment Variables (`.env`)

```bash
REDIS_HOST=localhost      # Redis host (connects to your options-data-b)
REDIS_PORT=6380          # Redis port (Docker mapped port)  
REDIS_DB=0               # Redis database number
API_PORT=8001            # Local API port
TUNNEL_NAME=options-ticker  # Cloudflare tunnel name
```

### Ticker Configuration (`allowed_tickers.json`)

Add or remove ticker/date combinations as needed:

```json
{
  "allowed": [
    {"asset": "BTC", "expiry": "29DEC23"},
    {"asset": "ETH", "expiry": "29DEC23"}, 
    {"asset": "SOL", "expiry": "29DEC23"},
    {"asset": "BTC", "expiry": "5JAN24"}
  ]
}
```

The API automatically reloads this configuration on each request.

### Cloudflare Tunnel (`config.yml`)

```yaml
tunnel: your-tunnel-id-here
credentials-file: /Users/anujsainicse/.cloudflared/your-tunnel-id-here.json

ingress:
  - hostname: ticker.yourdomain.com
    service: http://localhost:8001
  - service: http_status:404
```

## 🔒 Security Features

- **Filtered Access**: Only configured ticker/date combinations are accessible
- **404 for Non-Configured**: Returns 404 for any non-allowed combinations  
- **HTTPS by Default**: Cloudflare provides automatic HTTPS
- **DDoS Protection**: Cloudflare handles traffic protection
- **No Database Exposure**: Redis is never directly accessible

## 🧪 Testing

### Local Testing

```bash
# Start API only (without tunnel)
python tunnel_api.py

# Test endpoints
curl http://localhost:8001/
curl http://localhost:8001/config
curl http://localhost:8001/health
curl http://localhost:8001/ticker/BTC/29DEC23
```

### Remote Testing

```bash
# Test public endpoints (replace with your domain)
curl https://ticker.yourdomain.com/
curl https://ticker.yourdomain.com/ticker/BTC/29DEC23
```

## 📊 Monitoring

### Health Check

```bash
curl https://ticker.yourdomain.com/health
```

Returns:
```json
{
  "status": "healthy",
  "database": "connected",
  "configuration": "loaded", 
  "available_tickers": 3,
  "timestamp": "2023-12-20T15:30:00.123456"
}
```

### Configuration Status

```bash
curl https://ticker.yourdomain.com/config
```

Shows current configuration and database statistics.

## 🛠 Troubleshooting

### Common Issues

1. **API won't start**: Check if port 8001 is available
2. **Database connection failed**: Ensure options-data-b Docker containers are running
3. **Cloudflare tunnel fails**: Verify tunnel ID and credentials in config.yml
4. **404 for valid ticker**: Check that the combination exists in allowed_tickers.json

### Debug Commands

```bash
# Check if Redis is accessible
python -c "from external_db_access import test_connection; print(test_connection())"

# Test API locally
curl http://localhost:8001/health

# Check tunnel status
cloudflared tunnel info options-ticker
```

### Logs

- API logs: Console output when running tunnel_api.py
- Tunnel logs: Console output when running cloudflared
- Optional: Configure file logging in config.yml

## 🔄 Updates

### Adding New Ticker/Date Combinations

1. Edit `allowed_tickers.json`
2. Add new entries to the "allowed" array
3. The API automatically picks up changes (no restart needed)

Example:
```json
{
  "allowed": [
    {"asset": "BTC", "expiry": "29DEC23"},
    {"asset": "NEW_ASSET", "expiry": "15JAN24"}  // Add this line
  ]
}
```

### Removing Access

1. Edit `allowed_tickers.json`
2. Remove entries or set to empty array
3. Changes take effect immediately

## 📁 Dependencies

- **FastAPI**: Web framework for the API
- **Uvicorn**: ASGI server
- **Redis**: Python client for database access
- **python-dotenv**: Environment variable management
- **Cloudflared**: Cloudflare tunnel client (installed separately)

## 🌐 Production Considerations

- Monitor API performance and database connections
- Set up alerting for tunnel health
- Consider rate limiting if needed (can be added via Cloudflare)
- Regularly update allowed ticker configurations
- Monitor logs for errors or unusual access patterns