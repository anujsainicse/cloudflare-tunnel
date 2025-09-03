#!/usr/bin/env python3
"""
Cloudflare Tunnel API for Bybit Options Data
Only serves data for configured ticker/date combinations
"""

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
load_dotenv()

import json
import os
from datetime import datetime
from typing import Dict, List
from external_db_access import connect_to_database

# Initialize FastAPI app
app = FastAPI(
    title="Options Ticker Tunnel API",
    description="Public API serving filtered options data via Cloudflare tunnel",
    version="1.0.0"
)

def load_config() -> Dict:
    """Load allowed ticker/date combinations from config file"""
    try:
        with open('allowed_tickers.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"allowed": []}
    except json.JSONDecodeError:
        return {"allowed": []}

def is_allowed(asset: str, expiry: str) -> bool:
    """Check if asset/expiry combination is allowed"""
    config = load_config()
    for item in config.get('allowed', []):
        if item.get('asset', '').upper() == asset.upper() and item.get('expiry', '') == expiry:
            return True
    return False

@app.get("/")
async def root():
    """API root endpoint"""
    config = load_config()
    return {
        "service": "Options Ticker Tunnel API",
        "status": "running",
        "description": "Public API serving filtered options data",
        "available_combinations": len(config.get('allowed', [])),
        "endpoints": {
            "ticker": "/ticker/{asset}/{expiry}",
            "config": "/config"
        }
    }

@app.get("/ticker/{asset}/{expiry}")
async def get_ticker(asset: str, expiry: str):
    """Get options for specific asset and expiry (if allowed)"""
    
    # Check if this combination is in config file
    if not is_allowed(asset, expiry):
        raise HTTPException(
            status_code=404, 
            detail=f"Ticker/date combination {asset}/{expiry} is not available"
        )
    
    try:
        # Connect to Redis database
        db = connect_to_database()
        
        if not db.is_connected():
            raise HTTPException(
                status_code=503,
                detail="Database connection failed"
            )
        
        # Get options data for the specific expiry and asset
        options = db.get_options_by_expiry(expiry, asset)
        
        # Calculate summary stats
        total_volume = sum(float(opt.get('volume_24h', 0)) for opt in options)
        total_open_interest = sum(float(opt.get('open_interest', 0)) for opt in options)
        
        call_options = [opt for opt in options if opt['symbol'].endswith('-C')]
        put_options = [opt for opt in options if opt['symbol'].endswith('-P')]
        
        return {
            "asset": asset.upper(),
            "expiry": expiry,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_options": len(options),
                "call_options": len(call_options),
                "put_options": len(put_options),
                "total_volume_24h": round(total_volume, 2),
                "total_open_interest": round(total_open_interest, 2)
            },
            "options": options
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving data: {str(e)}"
        )
    finally:
        # Close database connection
        try:
            db.close()
        except:
            pass

@app.get("/config")
async def show_config():
    """Show current configuration (which tickers/dates are available)"""
    config = load_config()
    
    # Also get database stats to show system health
    try:
        db = connect_to_database()
        db_connected = db.is_connected()
        if db_connected:
            stats = db.get_stats()
        else:
            stats = {"error": "Database not connected"}
        db.close()
    except Exception as e:
        db_connected = False
        stats = {"error": str(e)}
    
    return {
        "configuration": config,
        "database_status": "connected" if db_connected else "disconnected",
        "database_stats": stats,
        "last_updated": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db = connect_to_database()
        db_ok = db.is_connected()
        
        config = load_config()
        config_ok = len(config.get('allowed', [])) > 0
        
        return {
            "status": "healthy" if (db_ok and config_ok) else "unhealthy",
            "database": "connected" if db_ok else "disconnected",
            "configuration": "loaded" if config_ok else "empty",
            "available_tickers": len(config.get('allowed', [])),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('API_PORT', 8001))
    
    print(f"Starting Options Ticker Tunnel API on port {port}")
    print("Available endpoints:")
    print("  GET / - API information")
    print("  GET /ticker/{asset}/{expiry} - Get options data (if allowed)")
    print("  GET /config - Show configuration")
    print("  GET /health - Health check")
    print()
    print("To configure allowed tickers, edit: allowed_tickers.json")
    
    uvicorn.run(
        "tunnel_api:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True,
        log_level="info"
    )