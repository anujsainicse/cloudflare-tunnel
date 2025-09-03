#!/usr/bin/env python3
"""
External Database Access for Bybit Options Data
Simplified interface for other scripts to access the Redis database
"""

import redis
import json
from typing import Dict, List, Optional, Union
from datetime import datetime
import logging
from db_config import RedisConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptionsDatabase:
    """Simple interface to access options data from external scripts"""
    
    def __init__(self, **connection_overrides):
        """
        Initialize database connection
        
        Args:
            **connection_overrides: Override default Redis connection settings
        """
        self.redis_client = None
        self.connection_params = RedisConfig.get_connection_params(**connection_overrides)
        self._connect()
    
    def _connect(self) -> bool:
        """
        Establish Redis connection with fallback options
        
        Returns:
            bool: True if connected successfully
        """
        # Try primary configuration first
        if self._try_connect(self.connection_params):
            logger.info(f"Connected to Redis at {self.connection_params['host']}:{self.connection_params['port']}")
            return True
        
        # Try fallback configurations
        logger.warning("Primary connection failed, trying fallbacks...")
        for config in RedisConfig.get_fallback_configs():
            if self._try_connect(config):
                self.connection_params = config
                logger.info(f"Connected using fallback: {config['host']}:{config['port']}")
                return True
        
        logger.error("All connection attempts failed")
        return False
    
    def _try_connect(self, config: Dict) -> bool:
        """Try connecting with specific configuration"""
        try:
            client = redis.Redis(**config)
            client.ping()  # Test connection
            self.redis_client = client
            return True
        except Exception as e:
            logger.debug(f"Connection failed for {config['host']}:{config['port']} - {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if database is connected and responsive"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to database"""
        logger.info("Attempting to reconnect...")
        return self._connect()
    
    # ==================== Basic Data Access ====================
    
    def get_option(self, symbol: str) -> Dict:
        """
        Get single option data by symbol
        
        Args:
            symbol: Option symbol (e.g., "BTC-29DEC23-50000-C")
            
        Returns:
            Dict containing option data, empty if not found
        """
        if not self.is_connected():
            logger.error("Database not connected")
            return {}
        
        try:
            data = self.redis_client.hgetall(f"option:{symbol}")
            return self._parse_option_data(data) if data else {}
        except Exception as e:
            logger.error(f"Error getting option {symbol}: {e}")
            return {}
    
    def get_all_symbols(self, asset: str = None) -> List[str]:
        """
        Get all option symbols
        
        Args:
            asset: Filter by asset (BTC, ETH, SOL), None for all
            
        Returns:
            List of option symbols
        """
        if not self.is_connected():
            logger.error("Database not connected")
            return []
        
        try:
            pattern = f"option:{asset}-*" if asset else "option:*"
            keys = self.redis_client.keys(pattern)
            return [key.replace("option:", "") for key in keys]
        except Exception as e:
            logger.error(f"Error getting symbols: {e}")
            return []
    
    def get_options_by_asset(self, asset: str) -> List[Dict]:
        """
        Get all options for a specific asset
        
        Args:
            asset: Asset symbol (BTC, ETH, SOL)
            
        Returns:
            List of option data dictionaries
        """
        symbols = self.get_all_symbols(asset)
        options = []
        
        for symbol in symbols:
            data = self.get_option(symbol)
            if data:
                options.append(data)
        
        return options
    
    def get_options_by_expiry(self, expiry: str, asset: str = None) -> List[Dict]:
        """
        Get all options for a specific expiry date
        
        Args:
            expiry: Expiry date string (e.g., "29DEC23")
            asset: Filter by asset, None for all assets
            
        Returns:
            List of option data dictionaries
        """
        all_symbols = self.get_all_symbols(asset)
        options = []
        
        for symbol in all_symbols:
            if f"-{expiry}-" in symbol:
                data = self.get_option(symbol)
                if data:
                    options.append(data)
        
        return options
    
    def get_stats(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Dict with database statistics
        """
        if not self.is_connected():
            return {"error": "Database not connected"}
        
        try:
            stats = {
                'total_options': len(self.get_all_symbols()),
                'btc_options': len(self.get_all_symbols('BTC')),
                'eth_options': len(self.get_all_symbols('ETH')),
                'sol_options': len(self.get_all_symbols('SOL')),
                'connection': f"{self.connection_params['host']}:{self.connection_params['port']}",
                'database': self.connection_params['db'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Try to get additional stats from Redis
            try:
                global_stats = self.redis_client.hgetall("stats:global")
                if global_stats:
                    stats.update({
                        'messages_processed': int(global_stats.get('messages', 0)),
                        'last_update': global_stats.get('last_update', 'N/A')
                    })
            except:
                pass
                
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
    
    # ==================== Filtered Queries ====================
    
    def get_high_volume_options(self, min_volume: float = 100000, asset: str = None) -> List[Dict]:
        """Get options with high trading volume"""
        options = self.get_options_by_asset(asset) if asset else self.get_all_options()
        return [opt for opt in options if float(opt.get('volume_24h', 0)) >= min_volume]
    
    def get_high_iv_options(self, min_iv: float = 1.0, asset: str = None) -> List[Dict]:
        """Get options with high implied volatility"""
        options = self.get_options_by_asset(asset) if asset else self.get_all_options()
        return [opt for opt in options if float(opt.get('mark_iv', 0)) >= min_iv]
    
    def get_all_options(self) -> List[Dict]:
        """Get all options data"""
        symbols = self.get_all_symbols()
        options = []
        for symbol in symbols:
            data = self.get_option(symbol)
            if data:
                options.append(data)
        return options
    
    # ==================== Helper Methods ====================
    
    def _parse_option_data(self, data: Dict) -> Dict:
        """Parse option data with type conversion"""
        if not data:
            return {}
        
        parsed = {'symbol': data.get('symbol', '')}
        
        # Convert numeric fields
        float_fields = [
            'last_price', 'mark_price', 'index_price', 'mark_iv',
            'underlying_price', 'bid_price', 'ask_price', 'open_interest',
            'volume_24h', 'turnover_24h', 'delta', 'gamma', 'theta', 'vega',
            'bid_size', 'ask_size', 'bid_iv', 'ask_iv'
        ]
        
        for field in float_fields:
            if field in data:
                try:
                    parsed[field] = float(data[field])
                except (ValueError, TypeError):
                    parsed[field] = 0.0
        
        # Convert timestamp
        if 'timestamp' in data:
            try:
                parsed['timestamp'] = float(data['timestamp'])
            except:
                parsed['timestamp'] = 0
        
        return parsed
    
    def close(self):
        """Close database connection"""
        if self.redis_client:
            try:
                self.redis_client.close()
            except:
                pass
            self.redis_client = None


# ==================== Convenience Functions ====================

def connect_to_database(**kwargs) -> OptionsDatabase:
    """
    Quick function to connect to the options database
    
    Returns:
        OptionsDatabase instance
    """
    return OptionsDatabase(**kwargs)

def get_database_stats() -> Dict:
    """Quick function to get database statistics"""
    db = connect_to_database()
    return db.get_stats()

def get_all_btc_options() -> List[Dict]:
    """Quick function to get all BTC options"""
    db = connect_to_database()
    return db.get_options_by_asset('BTC')

def get_all_eth_options() -> List[Dict]:
    """Quick function to get all ETH options"""
    db = connect_to_database()
    return db.get_options_by_asset('ETH')

def get_all_sol_options() -> List[Dict]:
    """Quick function to get all SOL options"""
    db = connect_to_database()
    return db.get_options_by_asset('SOL')

def test_connection() -> bool:
    """Test if database connection is working"""
    db = connect_to_database()
    return db.is_connected()