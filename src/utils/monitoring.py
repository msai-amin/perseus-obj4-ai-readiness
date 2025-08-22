#!/usr/bin/env python3
"""
KG-Perseus Monitoring and Performance Tracking
Provides monitoring, logging, and performance tracking utilities.
"""

import logging
import time
import os
import sys
from functools import wraps
from typing import Callable, Any, Dict, Optional
from pathlib import Path
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Performance monitoring and tracking utility."""
    
    def __init__(self, log_dir: Path = None):
        self.log_dir = log_dir or Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        self.performance_log = []
    
    def monitor_performance(self, func: Callable) -> Callable:
        """Decorator to monitor function performance."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                end_memory = self._get_memory_usage()
                memory_used = end_memory - start_memory
                
                # Log performance metrics
                performance_data = {
                    'function': func.__name__,
                    'execution_time': execution_time,
                    'memory_used_mb': memory_used,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                }
                
                self.performance_log.append(performance_data)
                logger.info(f"{func.__name__} completed in {execution_time:.2f} seconds, "
                          f"memory: {memory_used:.2f} MB")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                performance_data = {
                    'function': func.__name__,
                    'execution_time': execution_time,
                    'memory_used_mb': 0,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.performance_log.append(performance_data)
                logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {e}")
                raise
                
        return wrapper
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return 0.0
    
    def save_performance_log(self, filename: str = None):
        """Save performance log to file."""
        if filename is None:
            filename = f"performance_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_file = self.log_dir / filename
        
        try:
            with open(log_file, 'w') as f:
                json.dump(self.performance_log, f, indent=2)
            logger.info(f"Performance log saved to: {log_file}")
        except Exception as e:
            logger.error(f"Failed to save performance log: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self.performance_log:
            return {}
        
        successful_runs = [log for log in self.performance_log if log['status'] == 'success']
        failed_runs = [log for log in self.performance_log if log['status'] == 'error']
        
        if successful_runs:
            execution_times = [log['execution_time'] for log in successful_runs]
            memory_usage = [log['memory_used_mb'] for log in successful_runs]
            
            summary = {
                'total_runs': len(self.performance_log),
                'successful_runs': len(successful_runs),
                'failed_runs': len(failed_runs),
                'success_rate': len(successful_runs) / len(self.performance_log) * 100,
                'avg_execution_time': sum(execution_times) / len(execution_times),
                'max_execution_time': max(execution_times),
                'min_execution_time': min(execution_times),
                'avg_memory_usage': sum(memory_usage) / len(memory_usage),
                'max_memory_usage': max(memory_usage)
            }
        else:
            summary = {
                'total_runs': len(self.performance_log),
                'successful_runs': 0,
                'failed_runs': len(failed_runs),
                'success_rate': 0
            }
        
        return summary

class ErrorHandler:
    """Error handling and recovery utility."""
    
    def __init__(self, log_dir: Path = None):
        self.log_dir = log_dir or Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        self.error_log = []
    
    def handle_errors(self, func: Callable) -> Callable:
        """Decorator to handle errors gracefully."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_data = {
                    'function': func.__name__,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.error_log.append(error_data)
                logger.error(f"Error in {func.__name__}: {e}")
                
                # Log to file
                error_file = self.log_dir / 'error_log.json'
                try:
                    with open(error_file, 'w') as f:
                        json.dump(self.error_log, f, indent=2)
                except Exception as log_error:
                    logger.error(f"Failed to save error log: {log_error}")
                
                raise
                
        return wrapper
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics."""
        if not self.error_log:
            return {}
        
        error_types = {}
        for error in self.error_log:
            error_type = error['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': len(self.error_log),
            'error_types': error_types,
            'most_common_error': max(error_types.items(), key=lambda x: x[1]) if error_types else None
        }

class DataQualityMonitor:
    """Data quality monitoring utility."""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path('data')
        self.quality_log = []
    
    def monitor_data_quality(self, data: Any, data_name: str) -> Dict[str, Any]:
        """Monitor data quality metrics."""
        quality_metrics = {
            'data_name': data_name,
            'timestamp': datetime.now().isoformat(),
            'is_valid': True,
            'issues': []
        }
        
        try:
            if hasattr(data, 'shape'):  # DataFrame
                quality_metrics.update({
                    'row_count': data.shape[0],
                    'column_count': data.shape[1],
                    'empty_cells': data.isnull().sum().sum(),
                    'duplicate_rows': data.duplicated().sum()
                })
                
                if data.empty:
                    quality_metrics['is_valid'] = False
                    quality_metrics['issues'].append("Data is empty")
                
                if data.isnull().sum().sum() > data.shape[0] * data.shape[1] * 0.1:
                    quality_metrics['issues'].append("High percentage of missing values")
                
            elif isinstance(data, dict):
                quality_metrics.update({
                    'key_count': len(data),
                    'has_entities': 'entities' in data,
                    'has_relationships': 'relationships' in data
                })
                
                if not data:
                    quality_metrics['is_valid'] = False
                    quality_metrics['issues'].append("Dictionary is empty")
                
            elif isinstance(data, list):
                quality_metrics.update({
                    'item_count': len(data)
                })
                
                if not data:
                    quality_metrics['is_valid'] = False
                    quality_metrics['issues'].append("List is empty")
            
        except Exception as e:
            quality_metrics['is_valid'] = False
            quality_metrics['issues'].append(f"Error analyzing data: {e}")
        
        self.quality_log.append(quality_metrics)
        return quality_metrics
    
    def save_quality_report(self, filename: str = None):
        """Save data quality report."""
        if filename is None:
            filename = f"data_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_file = self.data_dir / 'outputs' / filename
        report_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(report_file, 'w') as f:
                json.dump(self.quality_log, f, indent=2)
            logger.info(f"Data quality report saved to: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save quality report: {e}")

# Global instances
performance_monitor = PerformanceMonitor()
error_handler = ErrorHandler()
data_quality_monitor = DataQualityMonitor()

def setup_logging(log_level: str = 'INFO', log_file: str = None):
    """Setup comprehensive logging configuration."""
    if log_file is None:
        log_file = 'logs/analysis.log'
    
    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger.info(f"Logging configured - Level: {log_level}, File: {log_file}")

def log_function_call(func: Callable) -> Callable:
    """Decorator to log function calls."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger.info(f"Calling function: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} failed: {e}")
            raise
    return wrapper 