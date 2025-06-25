import logging
import logging.handlers
import json
import traceback
from datetime import datetime
from pathlib import Path
import os

class ATSLogger:
    """Centralized logging system for ATS application"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create main logger
        self.logger = logging.getLogger('ats')
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup file and console handlers"""
        
        # File handler with rotation (10MB max, keep 5 files)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "ats.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _format_message(self, category, action, details=None, error=None):
        """Format log message with structured data"""
        message_data = {
            "category": category,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        if error:
            message_data["error"] = str(error)
            message_data["traceback"] = traceback.format_exc()
        
        return json.dumps(message_data, indent=2)
    
    def info(self, category, action, details=None):
        """Log info level message"""
        message = self._format_message(category, action, details)
        self.logger.info(message)
    
    def warning(self, category, action, details=None):
        """Log warning level message"""
        message = self._format_message(category, action, details)
        self.logger.warning(message)
    
    def error(self, category, action, details=None, error=None):
        """Log error level message"""
        message = self._format_message(category, action, details, error)
        self.logger.error(message)
    
    def debug(self, category, action, details=None):
        """Log debug level message"""
        message = self._format_message(category, action, details)
        self.logger.debug(message)

# Global logger instance
logger = ATSLogger()

# Convenience functions for common logging patterns
def log_application_submit(company, title, app_id, is_duplicate=False):
    """Log application submission"""
    details = {
        "company": company,
        "title": title,
        "app_id": app_id,
        "is_duplicate": is_duplicate
    }
    level = logger.warning if is_duplicate else logger.info
    level("application", "submit", details)

def log_status_change(app_id, old_status, new_status, user_initiated=True):
    """Log status change"""
    details = {
        "app_id": app_id,
        "old_status": old_status,
        "new_status": new_status,
        "user_initiated": user_initiated
    }
    logger.info("status", "change", details)

def log_application_delete(app_id, company, title):
    """Log application deletion"""
    details = {
        "app_id": app_id,
        "company": company,
        "title": title
    }
    logger.info("application", "delete", details)

def log_database_error(operation, error, details=None):
    """Log database errors"""
    logger.error("database", operation, details, error)

def log_callback_error(callback_name, error, details=None):
    """Log callback errors"""
    logger.error("callback", callback_name, details, error)

def log_auto_update(updated_count, details=None):
    """Log auto-update operations"""
    if updated_count > 0:
        details = details or {}
        details["updated_count"] = updated_count
        logger.info("system", "auto_update", details)
    else:
        logger.debug("system", "auto_update", {"updated_count": 0})

def log_user_action(action, details=None):
    """Log user interactions"""
    logger.debug("user", action, details) 