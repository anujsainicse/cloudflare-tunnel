# API Examples & Usage

Complete examples of how to use the Options Ticker Tunnel API.

## 🌐 Base URLs

- **Local**: `http://localhost:8001`
- **Public**: `https://ticker.yourdomain.com` (replace with your domain)

## 📋 Available Endpoints

### 1. Root Endpoint
**GET /** - API information and status

```bash
curl https://ticker.yourdomain.com/
```

**Response:**
```json
{
  "service": "Options Ticker Tunnel API",
  "status": "running",
  "description": "Public API serving filtered options data",
  "available_combinations": 3,
  "endpoints": {
    "ticker": "/ticker/{asset}/{expiry}",
    "config": "/config"
  }
}
```

### 2. Health Check
**GET /health** - System health status

```bash
curl https://ticker.yourdomain.com/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "configuration": "loaded",
  "available_tickers": 3,
  "timestamp": "2025-09-03T18:20:06.767436"
}
```

### 3. Configuration
**GET /config** - Show current configuration and database stats

```bash
curl https://ticker.yourdomain.com/config
```

**Response:**
```json
{
  "configuration": {
    "allowed": [
      {"asset": "BTC", "expiry": "29DEC23"},
      {"asset": "ETH", "expiry": "29DEC23"},
      {"asset": "BTC", "expiry": "5JAN24"}
    ]
  },
  "database_status": "connected",
  "database_stats": {
    "total_options": 1900,
    "btc_options": 748,
    "eth_options": 804,
    "sol_options": 348,
    "connection": "localhost:6380",
    "database": 0,
    "timestamp": "2025-09-03T18:20:10.958598",
    "messages_processed": 13545086,
    "last_update": "1756903810.9438934"
  },
  "last_updated": "2025-09-03T18:20:10.959018"
}
```

### 4. Ticker Data
**GET /ticker/{asset}/{expiry}** - Get options data for specific ticker/date

```bash
# Valid request (if configured)
curl https://ticker.yourdomain.com/ticker/BTC/29DEC23

# Invalid request (not configured)  
curl https://ticker.yourdomain.com/ticker/SOL/15JAN24
```

**Success Response:**
```json
{
  "asset": "BTC",
  "expiry": "29DEC23", 
  "timestamp": "2025-09-03T18:20:14.884280",
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
      "index_price": 45000.0,
      "mark_iv": 0.85,
      "underlying_price": 45123.45,
      "bid_price": 1240.0,
      "ask_price": 1250.0,
      "open_interest": 150.5,
      "volume_24h": 125000.0,
      "turnover_24h": 5625000.0,
      "delta": 0.65,
      "gamma": 0.0023,
      "theta": -12.5,
      "vega": 0.45,
      "timestamp": 1703875200.0
    }
  ]
}
```

**Error Response (404):**
```json
{
  "detail": "Ticker/date combination SOL/15JAN24 is not available"
}
```

## 💻 Code Examples

### Python

```python
import requests
import json

# Base URL (replace with your domain)
BASE_URL = "https://ticker.yourdomain.com"

def get_ticker_data(asset, expiry):
    """Get options data for specific ticker/expiry"""
    url = f"{BASE_URL}/ticker/{asset}/{expiry}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print(f"Ticker/date {asset}/{expiry} not available")
        return None
    else:
        print(f"Error: {response.status_code}")
        return None

def check_health():
    """Check API health"""
    response = requests.get(f"{BASE_URL}/health")
    return response.json()

def get_available_tickers():
    """Get list of available ticker/date combinations"""
    response = requests.get(f"{BASE_URL}/config")
    data = response.json()
    return data['configuration']['allowed']

# Usage examples
if __name__ == "__main__":
    # Check health
    health = check_health()
    print("Health:", health['status'])
    
    # Get available combinations
    available = get_available_tickers()
    print("Available combinations:", len(available))
    
    # Get specific ticker data
    for combo in available:
        asset = combo['asset']
        expiry = combo['expiry']
        data = get_ticker_data(asset, expiry)
        
        if data:
            summary = data['summary']
            print(f"{asset} {expiry}: {summary['total_options']} options, "
                  f"${summary['total_volume_24h']:,.0f} volume")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'https://ticker.yourdomain.com';

async function getTickerData(asset, expiry) {
  try {
    const response = await axios.get(`${BASE_URL}/ticker/${asset}/${expiry}`);
    return response.data;
  } catch (error) {
    if (error.response?.status === 404) {
      console.log(`Ticker/date ${asset}/${expiry} not available`);
      return null;
    }
    throw error;
  }
}

async function checkHealth() {
  const response = await axios.get(`${BASE_URL}/health`);
  return response.data;
}

async function getAvailableTickers() {
  const response = await axios.get(`${BASE_URL}/config`);
  return response.data.configuration.allowed;
}

// Usage
async function main() {
  try {
    // Check health
    const health = await checkHealth();
    console.log('Health:', health.status);
    
    // Get available combinations  
    const available = await getAvailableTickers();
    console.log('Available combinations:', available.length);
    
    // Get data for each combination
    for (const combo of available) {
      const data = await getTickerData(combo.asset, combo.expiry);
      if (data) {
        const summary = data.summary;
        console.log(`${combo.asset} ${combo.expiry}: ${summary.total_options} options, $${summary.total_volume_24h.toLocaleString()} volume`);
      }
    }
  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();
```

### Bash/curl

```bash
#!/bin/bash

BASE_URL="https://ticker.yourdomain.com"

# Function to check health
check_health() {
    curl -s "$BASE_URL/health" | jq '.status'
}

# Function to get available tickers
get_available_tickers() {
    curl -s "$BASE_URL/config" | jq -r '.configuration.allowed[] | "\(.asset) \(.expiry)"'
}

# Function to get ticker data
get_ticker_data() {
    local asset=$1
    local expiry=$2
    curl -s "$BASE_URL/ticker/$asset/$expiry"
}

# Main script
echo "Health: $(check_health)"
echo ""
echo "Available tickers:"
get_available_tickers
echo ""

# Get data for first available ticker
FIRST_TICKER=$(get_available_tickers | head -1)
if [ ! -z "$FIRST_TICKER" ]; then
    ASSET=$(echo $FIRST_TICKER | cut -d' ' -f1)
    EXPIRY=$(echo $FIRST_TICKER | cut -d' ' -f2)
    
    echo "Getting data for $ASSET $EXPIRY:"
    get_ticker_data $ASSET $EXPIRY | jq '.summary'
fi
```

## 📊 Data Analysis Examples

### Calculate Total Market Activity

```python
import requests

def analyze_market_activity(base_url="https://ticker.yourdomain.com"):
    """Analyze total market activity across all available tickers"""
    
    # Get available combinations
    config_resp = requests.get(f"{base_url}/config")
    combinations = config_resp.json()['configuration']['allowed']
    
    total_options = 0
    total_volume = 0
    total_oi = 0
    
    results = []
    
    for combo in combinations:
        asset = combo['asset']
        expiry = combo['expiry']
        
        # Get ticker data
        resp = requests.get(f"{base_url}/ticker/{asset}/{expiry}")
        if resp.status_code == 200:
            data = resp.json()
            summary = data['summary']
            
            total_options += summary['total_options']
            total_volume += summary['total_volume_24h'] 
            total_oi += summary['total_open_interest']
            
            results.append({
                'asset': asset,
                'expiry': expiry,
                'options': summary['total_options'],
                'volume': summary['total_volume_24h'],
                'open_interest': summary['total_open_interest']
            })
    
    return {
        'totals': {
            'options': total_options,
            'volume': total_volume,
            'open_interest': total_oi
        },
        'breakdown': results
    }

# Usage
analysis = analyze_market_activity()
print(f"Total Options: {analysis['totals']['options']}")
print(f"Total Volume: ${analysis['totals']['volume']:,.2f}")
print(f"Total OI: ${analysis['totals']['open_interest']:,.2f}")
```

### Find High IV Options

```python
def find_high_iv_options(asset, expiry, min_iv=1.0, base_url="https://ticker.yourdomain.com"):
    """Find options with high implied volatility"""
    
    resp = requests.get(f"{base_url}/ticker/{asset}/{expiry}")
    if resp.status_code != 200:
        return []
    
    data = resp.json()
    high_iv_options = []
    
    for option in data['options']:
        iv = option.get('mark_iv', 0)
        if iv >= min_iv:
            high_iv_options.append({
                'symbol': option['symbol'],
                'iv': iv,
                'volume': option.get('volume_24h', 0),
                'price': option.get('mark_price', 0)
            })
    
    # Sort by IV descending
    high_iv_options.sort(key=lambda x: x['iv'], reverse=True)
    return high_iv_options

# Usage
high_iv = find_high_iv_options('BTC', '29DEC23', min_iv=0.8)
for option in high_iv[:5]:  # Top 5
    print(f"{option['symbol']}: {option['iv']:.1%} IV, ${option['volume']:,.0f} vol")
```

## 🔍 Monitoring Examples

### Health Check Script

```bash
#!/bin/bash
# health_monitor.sh - Monitor API health

BASE_URL="https://ticker.yourdomain.com"
LOG_FILE="health.log"

check_health() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local response=$(curl -s -w "%{http_code}" "$BASE_URL/health")
    local http_code="${response: -3}"
    local body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        local status=$(echo "$body" | jq -r '.status')
        echo "$timestamp - Health: $status (HTTP $http_code)" | tee -a $LOG_FILE
        return 0
    else
        echo "$timestamp - Health check failed (HTTP $http_code)" | tee -a $LOG_FILE
        return 1
    fi
}

# Run every 60 seconds
while true; do
    check_health
    sleep 60
done
```

### Data Freshness Monitor

```python
import requests
import time
from datetime import datetime

def monitor_data_freshness(base_url="https://ticker.yourdomain.com", max_age_minutes=5):
    """Monitor if data is fresh (updated recently)"""
    
    config_resp = requests.get(f"{base_url}/config")
    db_stats = config_resp.json()['database_stats']
    
    # Check last update timestamp
    last_update = float(db_stats.get('last_update', 0))
    current_time = time.time()
    
    age_minutes = (current_time - last_update) / 60
    
    status = "fresh" if age_minutes <= max_age_minutes else "stale"
    
    return {
        'status': status,
        'last_update': datetime.fromtimestamp(last_update).isoformat(),
        'age_minutes': round(age_minutes, 1),
        'max_age_minutes': max_age_minutes
    }

# Usage
freshness = monitor_data_freshness()
print(f"Data status: {freshness['status']}")
print(f"Last update: {freshness['last_update']}")
print(f"Age: {freshness['age_minutes']} minutes")
```

## 🚨 Error Handling Examples

### Robust Error Handling

```python
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class OptionsAPI:
    def __init__(self, base_url="https://ticker.yourdomain.com"):
        self.base_url = base_url
        self.session = self._create_session()
    
    def _create_session(self):
        """Create session with retries and timeout"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def get_ticker_data(self, asset, expiry, timeout=30):
        """Get ticker data with comprehensive error handling"""
        try:
            url = f"{self.base_url}/ticker/{asset}/{expiry}"
            response = self.session.get(url, timeout=timeout)
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            elif response.status_code == 404:
                return {'success': False, 'error': 'ticker_not_available', 'message': f'{asset}/{expiry} not configured'}
            elif response.status_code == 503:
                return {'success': False, 'error': 'database_unavailable', 'message': 'Database connection failed'}
            else:
                return {'success': False, 'error': 'http_error', 'message': f'HTTP {response.status_code}'}
                
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'timeout', 'message': 'Request timed out'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'connection', 'message': 'Connection failed'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': 'request', 'message': str(e)}
        except Exception as e:
            return {'success': False, 'error': 'unknown', 'message': str(e)}

# Usage with error handling
api = OptionsAPI()
result = api.get_ticker_data('BTC', '29DEC23')

if result['success']:
    data = result['data']
    print(f"Got {data['summary']['total_options']} options")
else:
    print(f"Error ({result['error']}): {result['message']}")
```

## 📈 Performance Examples

### Parallel Requests

```python
import asyncio
import aiohttp
import time

async def get_ticker_data_async(session, asset, expiry, base_url="https://ticker.yourdomain.com"):
    """Async function to get ticker data"""
    url = f"{base_url}/ticker/{asset}/{expiry}"
    
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None
    except Exception as e:
        print(f"Error getting {asset}/{expiry}: {e}")
        return None

async def get_all_data_parallel(base_url="https://ticker.yourdomain.com"):
    """Get all available ticker data in parallel"""
    
    # First get available combinations
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/config") as response:
            config = await response.json()
            combinations = config['configuration']['allowed']
    
    # Then get all data in parallel
    async with aiohttp.ClientSession() as session:
        tasks = [
            get_ticker_data_async(session, combo['asset'], combo['expiry'], base_url)
            for combo in combinations
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Filter out None results
        valid_results = [r for r in results if r is not None]
        
        return {
            'results': valid_results,
            'count': len(valid_results),
            'duration': end_time - start_time
        }

# Usage
async def main():
    data = await get_all_data_parallel()
    print(f"Retrieved {data['count']} datasets in {data['duration']:.2f} seconds")

# Run with: asyncio.run(main())
```

## 🧪 Testing Examples

### Unit Tests

```python
import unittest
import requests
from unittest.mock import patch, Mock

class TestOptionsAPI(unittest.TestCase):
    
    def setUp(self):
        self.base_url = "https://ticker.yourdomain.com"
    
    def test_health_check(self):
        """Test health endpoint returns expected structure"""
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('database', data)
        self.assertIn('timestamp', data)
    
    def test_config_endpoint(self):
        """Test config endpoint returns configuration"""
        response = requests.get(f"{self.base_url}/config")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('configuration', data)
        self.assertIn('allowed', data['configuration'])
        self.assertIsInstance(data['configuration']['allowed'], list)
    
    def test_ticker_endpoint_valid(self):
        """Test ticker endpoint with valid combination"""
        # First get a valid combination from config
        config_resp = requests.get(f"{self.base_url}/config")
        combinations = config_resp.json()['configuration']['allowed']
        
        if combinations:
            combo = combinations[0]
            response = requests.get(f"{self.base_url}/ticker/{combo['asset']}/{combo['expiry']}")
            
            # Should be 200 (data) or 200 (empty but valid structure)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn('asset', data)
            self.assertIn('expiry', data)
            self.assertIn('summary', data)
            self.assertIn('options', data)
    
    def test_ticker_endpoint_invalid(self):
        """Test ticker endpoint with invalid combination"""
        response = requests.get(f"{self.base_url}/ticker/INVALID/INVALID")
        self.assertEqual(response.status_code, 404)
        
        data = response.json()
        self.assertIn('detail', data)

if __name__ == '__main__':
    unittest.main()
```

---

**Need more examples?** Check the [README.md](README.md) for full documentation or [CLOUD.md](CLOUD.md) for Cloudflare setup details.