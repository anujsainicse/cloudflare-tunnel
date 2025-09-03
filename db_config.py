#!/usr/bin/env python3
"""
Redis Database Configuration for External Scripts
Provides connection settings for accessing the options database
"""

import os
from typing import Dict, Any

class RedisConfig:
    """Redis connection configuration"""
    
    # Default connection settings for the Docker setup
    DEFAULT_SETTINGS = {
        'host': 'localhost',
        'port': 6380,  # Mapped Docker port
        'db': 0,
        'password': None,
        'socket_timeout': 5,
        'socket_connect_timeout': 5,
        'socket_keepalive': True,
        'socket_keepalive_options': {},
        'decode_responses': True,
        'max_connections': 10
    }
    
    @classmethod
    def get_connection_params(cls, **overrides) -> Dict[str, Any]:
        """
        Get Redis connection parameters
        
        Args:
            **overrides: Override default settings
            
        Returns:
            Dict with Redis connection parameters
        """
        params = cls.DEFAULT_SETTINGS.copy()
        
        # Override with environment variables if set
        env_overrides = {
            'host': os.getenv('REDIS_HOST'),
            'port': int(os.getenv('REDIS_PORT', '0')) or None,
            'db': int(os.getenv('REDIS_DB', '0')) or None,
            'password': os.getenv('REDIS_PASSWORD')
        }
        
        # Apply non-None environment overrides
        for key, value in env_overrides.items():
            if value is not None:
                params[key] = value
        
        # Apply user overrides
        params.update(overrides)
        
        return params
    
    @classmethod
    def get_connection_url(cls, **overrides) -> str:
        """
        Get Redis connection URL
        
        Returns:
            Redis connection URL string
        """
        params = cls.get_connection_params(**overrides)
        
        if params['password']:
            return f"redis://:{params['password']}@{params['host']}:{params['port']}/{params['db']}"
        else:
            return f"redis://{params['host']}:{params['port']}/{params['db']}"
    
    @classmethod
    def is_docker_setup(cls) -> bool:
        """Check if we're likely using the Docker setup"""
        return cls.DEFAULT_SETTINGS['port'] == 6380
    
    @classmethod
    def get_fallback_configs(cls) -> list:
        """Get list of fallback connection configurations to try"""
        configs = []
        
        # Primary config (Docker setup)
        configs.append(cls.get_connection_params())
        
        # Fallback to standard Redis port
        configs.append(cls.get_connection_params(port=6379))
        
        # Local development setup
        if cls.is_docker_setup():
            configs.append({
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'decode_responses': True,
                'socket_timeout': 2
            })
        
        return configs