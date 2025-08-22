#!/usr/bin/env python3
"""
KG-Perseus Configuration Management
Centralized configuration for the project.
"""

import os
from pathlib import Path
from typing import Dict, Any
import yaml

class Config:
    """Centralized configuration management."""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or 'config/analysis_config.yaml'
        self.load_environment()
        self.load_config_file()
    
    def load_environment(self):
        """Load environment variables and configuration."""
        self.database_config = {
            'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7689'),
            'user': os.getenv('NEO4J_USER', 'neo4j'),
            'password': os.getenv('NEO4J_PASSWORD', 'perseus2025'),
            'database': os.getenv('NEO4J_DATABASE', 'neo4j')
        }
        
        self.paths = {
            'data_dir': Path(os.getenv('DATA_DIR', 'data')),
            'output_dir': Path(os.getenv('OUTPUT_DIR', 'data/outputs')),
            'logs_dir': Path(os.getenv('LOGS_DIR', 'logs')),
            'docs_dir': Path(os.getenv('DOCS_DIR', 'docs')),
            'config_dir': Path(os.getenv('CONFIG_DIR', 'config'))
        }
        
        self.analysis_config = {
            'batch_size': int(os.getenv('BATCH_SIZE', '100')),
            'timeout': int(os.getenv('TIMEOUT', '30')),
            'retry_attempts': int(os.getenv('RETRY_ATTEMPTS', '3')),
            'log_level': os.getenv('LOG_LEVEL', 'INFO')
        }
        
        # Create directories if they don't exist
        for path in self.paths.values():
            path.mkdir(parents=True, exist_ok=True)
    
    def load_config_file(self):
        """Load configuration from YAML file."""
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Update configurations with file data
                if 'database' in config_data:
                    self.database_config.update(config_data['database'])
                if 'analysis' in config_data:
                    self.analysis_config.update(config_data['analysis'])
                if 'logging' in config_data:
                    self.logging_config = config_data['logging']
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file."""
        default_config = {
            'database': {
                'uri': 'bolt://localhost:7689',
                'user': 'neo4j',
                'password': 'perseus2025',
                'timeout': 30
            },
            'analysis': {
                'batch_size': 100,
                'retry_attempts': 3,
                'output_format': 'csv',
                'include_visualizations': True
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'logs/analysis.log'
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            print(f"Created default config file: {self.config_file}")
        except Exception as e:
            print(f"Warning: Could not create config file: {e}")
    
    def get_database_uri(self) -> str:
        """Get database URI."""
        return self.database_config['uri']
    
    def get_database_auth(self) -> tuple:
        """Get database authentication."""
        return (self.database_config['user'], self.database_config['password'])
    
    def get_output_dir(self) -> Path:
        """Get output directory."""
        return self.paths['output_dir']
    
    def get_logs_dir(self) -> Path:
        """Get logs directory."""
        return self.paths['logs_dir']
    
    def get_batch_size(self) -> int:
        """Get batch size for processing."""
        return self.analysis_config['batch_size']
    
    def get_timeout(self) -> int:
        """Get timeout for operations."""
        return self.analysis_config['timeout']
    
    def get_retry_attempts(self) -> int:
        """Get number of retry attempts."""
        return self.analysis_config['retry_attempts']

# Global configuration instance
config = Config() 