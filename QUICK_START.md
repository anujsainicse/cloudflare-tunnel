# Quick Start Guide

Get your Cloudflare tunnel running in 5 minutes!

## 🚀 Step 1: Configure What to Expose

Edit `allowed_tickers.json`:

```json
{
  "allowed": [
    {"asset": "BTC", "expiry": "29DEC23"},
    {"asset": "ETH", "expiry": "29DEC23"}
  ]
}
```

## 🧪 Step 2: Test Locally

```bash
./start.sh
```

Wait for:
```
✅ API server started successfully
📊 Local API: http://localhost:8001
```

Test it:
```bash
curl http://localhost:8001/health
# Should return: {"status":"healthy"...}

curl http://localhost:8001/ticker/BTC/29DEC23
# Should return options data

curl http://localhost:8001/ticker/SOL/29DEC23
# Should return: {"detail":"Ticker/date combination SOL/29DEC23 is not available"}
```

## ☁️ Step 3: Set Up Cloudflare (One-Time)

### Install cloudflared
```bash
brew install cloudflare/cloudflare/cloudflared
```

### Create tunnel
```bash
cloudflared tunnel login
cloudflared tunnel create options-ticker
```

Copy the tunnel ID from output.

### Update config
Edit `config.yml` and replace `[TUNNEL_ID]` with your actual ID:
```yaml
tunnel: 12345678-1234-1234-1234-123456789abc
credentials-file: /Users/anujsainicse/.cloudflared/12345678-1234-1234-1234-123456789abc.json
```

Replace `ticker.yourdomain.com` with your domain.

### Create DNS
```bash
cloudflared tunnel route dns options-ticker ticker.yourdomain.com
```

## 🌐 Step 4: Go Live

```bash
./start.sh
```

Your API is now publicly accessible at:
- `https://ticker.yourdomain.com/health`
- `https://ticker.yourdomain.com/ticker/BTC/29DEC23`

## ✅ That's It!

Your filtered options data is now publicly available via Cloudflare tunnel!

To change what's exposed, just edit `allowed_tickers.json` - changes take effect immediately.

---

**Need help?** Check [CLOUD.md](CLOUD.md) for detailed setup or [README.md](README.md) for full documentation.