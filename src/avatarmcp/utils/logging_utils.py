import logging
import logging.handlers
import sys
from typing import Optional

def setup_logging(
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True,
    force_stderr: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB default
    backup_count: int = 5               # Keep 5 backup files
) -> None:
    """
    Set up logging configuration with file rotation and stderr output.
    
    Args:
        log_level: Logging level (default: logging.INFO)
        log_file: Optional path to log file (default: None)
        console: Whether to log to console (default: True)
        force_stderr: If True, force all logging to stderr (default: True)
        max_bytes: Maximum log file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add handlers
    handlers = []
    
    if console:
        # Create a stream handler that explicitly uses stderr
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(log_level)
        stderr_handler.setFormatter(formatter)
        handlers.append(stderr_handler)
    
    if log_file:
        try:
            # Use RotatingFileHandler for log rotation
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                mode='a',
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8',
                delay=False
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
            
            # Log the log file location at startup
            if console or force_stderr:
                # Use stderr directly for initial logging setup message only
                sys.stderr.write(f"Logging to file: {log_file}\n")
        except Exception as e:
            # Use stderr directly for critical setup errors
            sys.stderr.write(f"Failed to set up file logging: {e}\n")
    
    # Add all handlers to the root logger
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Force all logging to stderr if requested
    if force_stderr and console:
        # Redirect stdout to stderr to catch any print statements
        sys.stdout = sys.stderr
        
        # Also patch the root logger to ensure no handlers use stdout
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream is sys.__stdout__:
                handler.stream = sys.stderr
    
    # Set up asyncio logging
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    # Silence noisy loggers
    logging.getLogger('websockets').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    
    # Force any other loggers to use our configuration
    logging.captureWarnings(True)