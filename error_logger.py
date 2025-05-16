# error_logger.py
import logging
import os
import sys
import traceback
from datetime import datetime

LOG_FILENAME = 'cerberus_builder.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Determine the directory of the logger script itself
log_dir = os.path.dirname(__file__) if os.path.dirname(__file__) else '.'
log_filepath = os.path.join(log_dir, LOG_FILENAME)

# --- Basic Logger Setup ---
# Create logger
logger = logging.getLogger('cerberus_builder')
logger.setLevel(logging.DEBUG) # Log everything from DEBUG level up

# Prevent adding multiple handlers if this module is imported again elsewhere
if not logger.handlers:
    # --- File Handler ---
    # Rotates logs, keeping 1 backup, max 2MB per file
    # Use RotatingFileHandler for production to prevent huge log files
    # For simplicity now, using a regular FileHandler
    try:
        file_handler = logging.FileHandler(log_filepath, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO) # Log INFO, WARNING, ERROR, CRITICAL to file
        file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"[ERROR_LOGGER] CRITICAL: Failed to create file handler for {log_filepath}: {e}", file=sys.stderr)
        # Fallback or stop? For now, just print error.

    # --- Console Handler (Optional, but good for seeing errors immediately) ---
    console_handler = logging.StreamHandler(sys.stderr) # Log warnings/errors to console
    console_handler.setLevel(logging.WARNING) # Only show WARNING and above on console
    console_formatter = logging.Formatter('%(levelname)s: %(message)s') # Simpler format for console
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

# --- Logging Functions ---

def log_info(message):
    """Logs an informational message."""
    try:
        logger.info(message)
    except Exception as e:
        print(f"[ERROR_LOGGER] Failed to log INFO message: {e}", file=sys.stderr)

def log_warning(message):
    """Logs a warning message."""
    try:
        logger.warning(message)
    except Exception as e:
        print(f"[ERROR_LOGGER] Failed to log WARNING message: {e}", file=sys.stderr)

def log_error(message, exc_info=True):
    """Logs an error message, optionally including exception info."""
    try:
        # exc_info=True automatically adds exception info if called within an except block
        logger.error(message, exc_info=exc_info)
    except Exception as e:
        print(f"[ERROR_LOGGER] Failed to log ERROR message: {e}", file=sys.stderr)

def log_critical(message, exc_info=True):
    """Logs a critical error message."""
    try:
        logger.critical(message, exc_info=exc_info)
    except Exception as e:
        print(f"[ERROR_LOGGER] Failed to log CRITICAL message: {e}", file=sys.stderr)

def log_exception(message="An exception occurred"):
    """Convenience function to log an exception with full traceback."""
    try:
        # Automatically captures and formats the current exception traceback
        logger.exception(message)
    except Exception as e:
        print(f"[ERROR_LOGGER] Failed to log EXCEPTION: {e}", file=sys.stderr)


# --- Example Usage (if run directly) ---
if __name__ == '__main__':
    print(f"Logging configured. Log file location: {os.path.abspath(log_filepath)}")
    log_info("Logger test: Info message.")
    log_warning("Logger test: Warning message.")
    try:
        x = 1 / 0
    except ZeroDivisionError:
        log_error("Logger test: Error message with exception info.")
        log_exception("Logger test: Explicit exception log.") # More detailed

    log_critical("Logger test: Critical message.")
    print("Check the 'cerberus_builder.log' file.")