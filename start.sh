#!/bin/bash

# Cloudflare Tunnel Startup Script
# This script starts the API server and Cloudflare tunnel

echo "🚀 Starting Options Ticker Tunnel..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if config file exists
if [ ! -f "allowed_tickers.json" ]; then
    echo "❌ allowed_tickers.json not found!"
    echo "Please create the configuration file first."
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Start the API server in background
echo "🌐 Starting API server on port ${API_PORT:-8001}..."
python tunnel_api.py &
API_PID=$!

# Wait for API to start
echo "⏳ Waiting for API to initialize..."
sleep 3

# Test if API is running
if curl -s http://localhost:${API_PORT:-8001}/health > /dev/null; then
    echo "✅ API server started successfully"
else
    echo "❌ API server failed to start"
    kill $API_PID 2>/dev/null
    exit 1
fi

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared not found!"
    echo "Please install it first:"
    echo "  brew install cloudflare/cloudflare/cloudflared"
    kill $API_PID 2>/dev/null
    exit 1
fi

# Check if tunnel is configured
if [ ! -f "config.yml" ] || grep -q "\[TUNNEL_ID\]" config.yml; then
    echo "⚠️  Cloudflare tunnel not configured yet!"
    echo ""
    echo "To configure the tunnel:"
    echo "1. cloudflared tunnel login"
    echo "2. cloudflared tunnel create options-ticker"
    echo "3. Update config.yml with your tunnel ID and domain"
    echo "4. cloudflared tunnel route dns options-ticker ticker.yourdomain.com"
    echo ""
    echo "API is running at: http://localhost:${API_PORT:-8001}"
    echo "Press Ctrl+C to stop"
    
    # Keep API running for local testing
    wait $API_PID
    exit 0
fi

echo "🌩️  Starting Cloudflare tunnel..."
cloudflared tunnel --config config.yml run &
TUNNEL_PID=$!

echo ""
echo "✅ System started successfully!"
echo "📊 Local API: http://localhost:${API_PORT:-8001}"
echo "🌐 Public URL: Check your Cloudflare dashboard"
echo ""
echo "Available endpoints:"
echo "  GET / - API information"
echo "  GET /ticker/{asset}/{expiry} - Get options data"
echo "  GET /config - Show configuration"
echo "  GET /health - Health check"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop services
trap 'echo "🛑 Stopping services..."; kill $API_PID $TUNNEL_PID 2>/dev/null; exit 0' INT
wait