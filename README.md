# 🌩️ Cloudflare Tunnel for Options Data

> A secure, public API that serves filtered cryptocurrency options data via Cloudflare Tunnel. Only configured ticker/date combinations are exposed through HTTPS endpoints.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![Cloudflare](https://img.shields.io/badge/Cloudflare-Tunnel-orange.svg)](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)

## ✨ Features

- 🔒 **Secure by Default** - Only whitelisted ticker/date combinations are accessible
- 🚀 **FastAPI Backend** - High-performance async API with automatic docs
- 🌐 **Global CDN** - Powered by Cloudflare's global network
- 📊 **Real-time Data** - Live options data with strike prices, Greeks, and market metrics
- 🛡️ **DDoS Protection** - Built-in Cloudflare security features
- ⚡ **Zero Config SSL** - Automatic HTTPS certificates

## 🏗️ Architecture

```
Internet → Cloudflare CDN → Tunnel → Local API → Redis Database
```

## 📋 Prerequisites

- **Python 3.8+**
- **Redis Database** (with options data)
- **Cloudflare Account** with a domain
- **macOS/Linux** (Windows via WSL)

## 🚀 Quick Setup

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/cloudflare-tunnel.git
cd cloudflare-tunnel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Install Cloudflare CLI

```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Linux
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### 3. Configure Your Environment

Create `.env` file:
```bash
# Redis connection (adjust for your setup)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API settings
API_PORT=8002

# Cloudflare tunnel name
TUNNEL_NAME=your-tunnel-name
```

### 4. Set Up Cloudflare Tunnel

```bash
# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create your-tunnel-name

# Update config.yml with your tunnel ID and domain
# Replace placeholders in config.yml with actual values

# Create DNS route
cloudflared tunnel route dns your-tunnel-name api.yourdomain.com
```

### 5. Configure Data Access

Edit `allowed_tickers.json`:
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
    }
  ]
}
```

### 6. Launch

```bash
./start.sh
```

## 📚 API Documentation

### Base URL
```
https://your-domain.com
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and status |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/config` | Available ticker combinations |
| `GET` | `/ticker/{asset}/{expiry}` | Get options data for specific asset/expiry |

### Example Response

```json
{
  "asset": "ETH",
  "expiry": "5SEP25", 
  "timestamp": "2025-09-03T19:32:34.454169",
  "summary": {
    "total_options": 86,
    "call_options": 43,
    "put_options": 43,
    "total_volume_24h": 12483.2,
    "total_open_interest": 26902.7
  },
  "options": [
    {
      "symbol": "ETH-5SEP25-4800-C-USDT",
      "strike_price": 4800.0,
      "option_type": "C",
      "last_price": 4.4,
      "mark_price": 2.313266,
      "underlying_price": 4425.33,
      "delta": 0.03149913,
      "gamma": 0.00037049,
      "theta": -3.87452968,
      "vega": 0.21697459,
      "volume_24h": 340.3,
      "open_interest": 711.1
    }
  ]
}
```

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
REDIS_HOST=localhost          # Redis server host
REDIS_PORT=6379              # Redis server port  
REDIS_DB=0                   # Redis database number
API_PORT=8002                # Local API port
TUNNEL_NAME=your-tunnel      # Cloudflare tunnel name
```

### Tunnel Configuration (`config.yml`)

```yaml
tunnel: your-tunnel-id-here
credentials-file: /path/to/your/credentials.json

ingress:
  - hostname: api.yourdomain.com
    service: http://localhost:8002
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
  - service: http_status:404
```

### Data Filter (`allowed_tickers.json`)

Controls which ticker/expiry combinations are publicly accessible:

```json
{
  "allowed": [
    {"asset": "ETH", "expiry": "5SEP25"},
    {"asset": "BTC", "expiry": "26DEC25"}
  ]
}
```

## 🛡️ Security Features

- **Whitelist-Only Access** - Only configured combinations are accessible
- **Automatic 404s** - Non-whitelisted requests return 404
- **HTTPS Only** - All traffic encrypted via Cloudflare
- **DDoS Protection** - Built-in Cloudflare security
- **No Direct DB Access** - Redis never exposed directly

## 🔍 Monitoring

### Health Check
```bash
curl https://api.yourdomain.com/health
```

### View Configuration
```bash
curl https://api.yourdomain.com/config
```

### Check Tunnel Status
```bash
cloudflared tunnel info your-tunnel-name
```

## 🛠️ Development

### Local Testing
```bash
# Start API only (no tunnel)
python tunnel_api.py

# Test endpoints
curl http://localhost:8002/health
```

### Adding New Data
1. Update `allowed_tickers.json`
2. Changes take effect immediately (no restart needed)

### Logs
- API logs: Console output
- Tunnel logs: Console output when running cloudflared

## 📊 Data Format

### Redis Key Format
```
option:ASSET-EXPIRY-STRIKE-TYPE-CURRENCY
```
Example: `option:ETH-5SEP25-4800-C-USDT`

### Supported Assets
- BTC (Bitcoin)
- ETH (Ethereum)
- SOL (Solana)

### Date Formats
- Format: `5SEP25` (no leading zero)
- Examples: `5SEP25`, `26DEC25`, `31OCT25`

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
lsof -ti:8002  # Find process using port
kill -9 <PID> # Kill process
```

**2. Tunnel Connection Failed**
```bash
cloudflared tunnel info your-tunnel-name
cloudflared tunnel login  # Re-authenticate
```

**3. Empty Data Response**
- Check if expiry date exists in Redis
- Verify ticker is in `allowed_tickers.json`
- Use correct date format (no leading zeros)

**4. DNS Not Resolving**
- Wait for DNS propagation (up to 24 hours)
- Check Cloudflare DNS settings
- Verify tunnel route: `cloudflared tunnel route ip show`

### Debug Commands
```bash
# Test Redis connection
python -c "from external_db_access import test_connection; print(test_connection())"

# Check available Redis keys
redis-cli KEYS "option:*" | head -10

# Test local API
curl http://localhost:8002/health
```

## 📝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- 📖 [Documentation](docs/)
- 🐛 [Report Issues](https://github.com/yourusername/cloudflare-tunnel/issues)
- 💬 [Discussions](https://github.com/yourusername/cloudflare-tunnel/discussions)

## ⭐ Acknowledgments

- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/) for secure tunneling
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Redis](https://redis.io/) for data storage

---

Made with ❤️ for the crypto options community