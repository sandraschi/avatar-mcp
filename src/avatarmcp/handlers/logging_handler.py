"""
Logging handler for the Avatar MCP server.

This module provides a centralized logging system for the Avatar MCP server,
with support for multiple log destinations, log rotation, and structured logging.
"""

import asyncio
import logging
import logging.handlers
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Type, TypeVar, Tuple, Callable, Awaitable
from dataclasses import dataclass, field, asdict
import json
import traceback
import inspect
import threading
import queue

from .base_handler import BaseHandler

logger = logging.getLogger(__name__)

class LogLevel(str):
    """Log level with validation."""
    
    VALID_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    def __new__(cls, value: str) -> 'LogLevel':
        """Create a new LogLevel instance."""
        value = value.upper()
        if value not in cls.VALID_LEVELS:
            raise ValueError(f"Invalid log level: {value}. Must be one of: {', '.join(cls.VALID_LEVELS.keys())}")
        instance = super().__new__(cls, value)
        instance.level = cls.VALID_LEVELS[value]
        return instance

@dataclass
class LogMessage:
    """Structured log message."""
    
    timestamp: str
    level: str
    logger: str
    message: str
    module: str
    function: str
    line: int
    thread: int
    process: int
    extra: Dict[str, Any] = field(default_factory=dict)
    exception: Optional[str] = None
    stack_trace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_record(cls, record: logging.LogRecord) -> 'LogMessage':
        """Create from a logging.LogRecord."""
        extra = {}
        if hasattr(record, '__dict__'):
            # Filter out standard LogRecord attributes
            standard_attrs = set(vars(logging.LogRecord('', 0, '', 0, '', (), None, None)))
            extra = {
                k: v for k, v in record.__dict__.items()
                if k not in standard_attrs and not k.startswith('_')
            }
        
        # Get exception info if available
        exc_info = None
        stack_trace = None
        if record.exc_info:
            exc_info = str(record.exc_info[1])
            stack_trace = ''.join(traceback.format_exception(*record.exc_info))
        
        return cls(
            timestamp=datetime.fromtimestamp(record.created).isoformat(),
            level=record.levelname,
            logger=record.name,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line=record.lineno,
            thread=record.thread,
            process=record.process,
            extra=extra,
            exception=exc_info,
            stack_trace=stack_trace
        )

class LogHandler(logging.Handler):
    """Base class for log handlers."""
    
    def __init__(self, level: Union[int, str] = logging.NOTSET):
        """Initialize the log handler."""
        super().__init__(level)
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        try:
            self._emit(record)
        except Exception as e:
            print(f"Error in log handler: {str(e)}", file=sys.stderr)
    
    def _emit(self, record: logging.LogRecord) -> None:
        """Eit a log record (to be implemented by subclasses)."""
        raise NotImplementedError

class ConsoleLogHandler(LogHandler):
    """Log handler that writes to the console."""
    
    def __init__(self, level: Union[int, str] = logging.INFO):
        """Initialize the console log handler."""
        super().__init__(level)
        self.console = logging.StreamHandler()
        self.console.setFormatter(self.formatter)
    
    def _emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to the console."""
        self.console.emit(record)

class FileLogHandler(LogHandler):
    """Log handler that writes to a file with rotation."""
    
    def __init__(
        self,
        filename: str,
        level: Union[int, str] = logging.INFO,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        encoding: str = 'utf-8',
        delay: bool = False
    ):
        """Initialize the file log handler."""
        super().__init__(level)
        
        # Ensure directory exists
        log_dir = os.path.dirname(filename)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        self.handler = logging.handlers.RotatingFileHandler(
            filename=filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding,
            delay=delay
        )
        self.handler.setFormatter(self.formatter)
    
    def _emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to the file."""
        self.handler.emit(record)

class WebSocketLogHandler(LogHandler):
    """Log handler that broadcasts log messages via WebSocket."""
    
    def __init__(self, websocket_handler: Any, level: Union[int, str] = logging.INFO):
        """Initialize the WebSocket log handler.
        
        Args:
            websocket_handler: Instance of WebSocketHandler to use for broadcasting
        """
        super().__init__(level)
        self.websocket_handler = websocket_handler
    
    def _emit(self, record: logging.LogRecord) -> None:
        """Emit a log record via WebSocket."""
        if not hasattr(self.websocket_handler, 'broadcast'):
            return
        
        log_message = LogMessage.from_record(record)
        self.websocket_handler.broadcast({
            'type': 'log_message',
            'data': log_message.to_dict()
        }, topic='logs')

class QueueLogHandler(LogHandler):
    """Log handler that puts log messages in a queue for asynchronous processing."""
    
    def __init__(self, log_queue: 'asyncio.Queue[Dict[str, Any]]', level: Union[int, str] = logging.INFO):
        """Initialize the queue log handler.
        
        Args:
            log_queue: asyncio.Queue to put log messages in
        """
        super().__init__(level)
        self.log_queue = log_queue
    
    def _emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to the queue."""
        log_message = LogMessage.from_record(record)
        try:
            # Put the log message in the queue (non-blocking)
            self.log_queue.put_nowait(log_message.to_dict())
        except asyncio.QueueFull:
            # If the queue is full, drop the message
            print(f"Log queue full, dropping message: {log_message.message}", file=sys.stderr)

class LoggingHandler(BaseHandler):
    """Centralized logging handler for the Avatar MCP server."""
    
    def __init__(self, server: Any = None):
        """Initialize the logging handler.
        
        Args:
            server: Reference to the main server instance
        """
        super().__init__(server)
        self._handlers: Dict[str, LogHandler] = {}
        self._log_queue: Optional[asyncio.Queue[Dict[str, Any]]] = None
        self._log_consumer_task: Optional[asyncio.Task] = None
        self._default_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self._log_dir: Optional[Path] = None
        self._configured = False
    
    async def _initialize(self) -> None:
        """Initialize the logging system."""
        # Create log directory if it doesn't exist
        self._log_dir = Path("logs")
        self._log_dir.mkdir(exist_ok=True)
        
        # Set up the root logger
        self._setup_root_logger()
        
        # Set up the log queue and consumer task
        self._log_queue = asyncio.Queue(maxsize=1000)
        self._log_consumer_task = asyncio.create_task(self._log_consumer())
        
        # Add default handlers
        self.add_console_handler()
        self.add_file_handler("avatarmcp.log")
        
        # Log startup message
        logger.info("Logging handler initialized")
        self._configured = True
    
    def _setup_root_logger(self) -> None:
        """Configure the root logger with default settings."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Remove any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Add a null handler to prevent "No handlers could be found" warnings
        if not root_logger.handlers:
            root_logger.addHandler(logging.NullHandler())
    
    async def _log_consumer(self) -> None:
        """Consume log messages from the queue and process them."""
        if not self._log_queue:
            return
        
        while True:
            try:
                # Get a log message from the queue
                log_data = await self._log_queue.get()
                
                # Process the log message (e.g., send to external services)
                await self._process_log_message(log_data)
                
                # Mark the task as done
                self._log_queue.task_done()
                
            except asyncio.CancelledError:
                # Shutdown requested
                break
            except Exception as e:
                print(f"Error in log consumer: {str(e)}", file=sys.stderr)
    
    async def _process_log_message(self, log_data: Dict[str, Any]) -> None:
        """Process a log message.
        
        Args:
            log_data: Log message data
        """
        # This method can be overridden to implement custom log processing
        pass
    
    def add_console_handler(
        self,
        level: Union[int, str] = logging.INFO,
        formatter: Optional[logging.Formatter] = None
    ) -> str:
        """Add a console log handler.
        
        Args:
            level: Log level
            formatter: Log formatter to use (defaults to the handler's formatter)
            
        Returns:
            Handler ID
        """
        handler_id = f"console_{len(self._handlers) + 1}"
        handler = ConsoleLogHandler(level=level)
        
        if formatter:
            handler.setFormatter(formatter)
        
        self._add_handler(handler_id, handler)
        return handler_id
    
    def add_file_handler(
        self,
        filename: str,
        level: Union[int, str] = logging.INFO,
        formatter: Optional[logging.Formatter] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        encoding: str = 'utf-8'
    ) -> str:
        """Add a file log handler with rotation.
        
        Args:
            filename: Log file name (relative to log directory)
            level: Log level
            formatter: Log formatter to use (defaults to the handler's formatter)
            max_bytes: Maximum log file size in bytes
            backup_count: Number of backup log files to keep
            encoding: File encoding
            
        Returns:
            Handler ID
        """
        # Make sure filename is a Path object and resolve it relative to log directory
        log_file = self._log_dir / filename if self._log_dir else Path(filename)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler_id = f"file_{len(self._handlers) + 1}"
        handler = FileLogHandler(
            filename=str(log_file),
            level=level,
            max_bytes=max_bytes,
            backup_count=backup_count,
            encoding=encoding
        )
        
        if formatter:
            handler.setFormatter(formatter)
        
        self._add_handler(handler_id, handler)
        return handler_id
    
    def add_websocket_handler(
        self,
        websocket_handler: Any,
        level: Union[int, str] = logging.INFO,
        formatter: Optional[logging.Formatter] = None
    ) -> str:
        """Add a WebSocket log handler.
        
        Args:
            websocket_handler: WebSocket handler instance
            level: Log level
            formatter: Log formatter to use (defaults to the handler's formatter)
            
        Returns:
            Handler ID
        """
        handler_id = f"websocket_{len(self._handlers) + 1}"
        handler = WebSocketLogHandler(websocket_handler=websocket_handler, level=level)
        
        if formatter:
            handler.setFormatter(formatter)
        
        self._add_handler(handler_id, handler)
        return handler_id
    
    def add_queue_handler(
        self,
        log_queue: Optional['asyncio.Queue[Dict[str, Any]]'] = None,
        level: Union[int, str] = logging.INFO,
        formatter: Optional[logging.Formatter] = None
    ) -> str:
        """Add a queue log handler.
        
        Args:
            log_queue: asyncio.Queue to put log messages in (uses internal queue if None)
            level: Log level
            formatter: Log formatter to use (defaults to the handler's formatter)
            
        Returns:
            Handler ID
        """
        handler_id = f"queue_{len(self._handlers) + 1}"
        queue_to_use = log_queue if log_queue is not None else self._log_queue
        
        if queue_to_use is None:
            raise ValueError("No log queue provided and no default queue available")
        
        handler = QueueLogHandler(log_queue=queue_to_use, level=level)
        
        if formatter:
            handler.setFormatter(formatter)
        
        self._add_handler(handler_id, handler)
        return handler_id
    
    def _add_handler(self, handler_id: str, handler: LogHandler) -> None:
        """Add a handler to the root logger and internal registry."""
        if not isinstance(handler, LogHandler):
            raise ValueError("Handler must be an instance of LogHandler")
        
        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        
        # Store reference
        self._handlers[handler_id] = handler
    
    def remove_handler(self, handler_id: str) -> bool:
        """Remove a log handler.
        
        Args:
            handler_id: ID of the handler to remove
            
        Returns:
            True if the handler was removed, False otherwise
        """
        if handler_id not in self._handlers:
            return False
        
        # Remove from root logger
        root_logger = logging.getLogger()
        handler = self._handlers[handler_id]
        root_logger.removeHandler(handler)
        
        # Remove from registry
        del self._handlers[handler_id]
        return True
    
    def get_handler(self, handler_id: str) -> Optional[LogHandler]:
        """Get a log handler by ID.
        
        Args:
            handler_id: ID of the handler to get
            
        Returns:
            The handler, or None if not found
        """
        return self._handlers.get(handler_id)
    
    def set_level(self, handler_id: str, level: Union[int, str]) -> bool:
        """Set the log level for a handler.
        
        Args:
            handler_id: ID of the handler
            level: New log level (int or string)
            
        Returns:
            True if the level was set, False if the handler was not found
        """
        if handler_id not in self._handlers:
            return False
        
        if isinstance(level, str):
            level = logging.getLevelName(level.upper())
        
        self._handlers[handler_id].setLevel(level)
        return True
    
    def set_formatter(self, handler_id: str, formatter: logging.Formatter) -> bool:
        """Set the formatter for a handler.
        
        Args:
            handler_id: ID of the handler
            formatter: New formatter
            
        Returns:
            True if the formatter was set, False if the handler was not found
        """
        if handler_id not in self._handlers:
            return False
        
        self._handlers[handler_id].setFormatter(formatter)
        return True
    
    def get_log_queue(self) -> Optional['asyncio.Queue[Dict[str, Any]]']:
        """Get the internal log queue.
        
        Returns:
            The log queue, or None if not available
        """
        return self._log_queue
    
    def get_log_directory(self) -> Optional[Path]:
        """Get the log directory.
        
        Returns:
            The log directory path, or None if not set
        """
        return self._log_dir
    
    def is_configured(self) -> bool:
        """Check if the logging system is configured.
        
        Returns:
            True if configured, False otherwise
        """
        return self._configured
    
    async def shutdown(self) -> None:
        """Clean up resources used by the logging handler."""
        # Cancel the log consumer task
        if self._log_consumer_task and not self._log_consumer_task.done():
            self._log_consumer_task.cancel()
            try:
                await self._log_consumer_task
            except asyncio.CancelledError:
                pass
            self._log_consumer_task = None
        
        # Clear handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        self._handlers.clear()
        self._log_queue = None
        self._configured = False
        
        logger.info("Logging handler shutdown complete")

# Helper functions for easy access
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Logger name (defaults to the caller's module name)
        
    Returns:
        A logger instance
    """
    if name is None:
        # Get the caller's module name
        frame = inspect.currentframe()
        try:
            frame = frame.f_back if frame else None
            module = inspect.getmodule(frame)
            name = module.__name__ if module else __name__
        finally:
            del frame  # Avoid reference cycles
    
    return logging.getLogger(name)

def setup_basic_logging(level: Union[int, str] = logging.INFO) -> None:
    """Set up basic logging configuration.
    
    Args:
        level: Log level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

class LogContext:
    """Context manager for logging with a specific logger and extra fields."""
    
    def __init__(
        self,
        logger: logging.Logger,
        message: str,
        level: int = logging.INFO,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize the log context.
        
        Args:
            logger: Logger instance to use
            message: Log message (may contain format placeholders)
            level: Log level (default: INFO)
            extra: Additional fields to include in the log record
            **kwargs: Format arguments for the log message
        """
        self.logger = logger
        self.message = message
        self.level = level
        self.extra = extra or {}
        self.kwargs = kwargs
        self.start_time = None
    
    def __enter__(self):
        """Enter the context and log the start message."""
        self.start_time = time.time()
        if self.logger.isEnabledFor(self.level):
            extra = self.extra.copy()
            extra.update({
                'action': 'start',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
            self.logger.log(
                self.level,
                f"START: {self.message}".format(**self.kwargs),
                extra=extra
            )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and log the end message with duration."""
        if self.start_time is None:
            return
        
        duration = time.time() - self.start_time
        level = logging.ERROR if exc_type else self.level
        
        if self.logger.isEnabledFor(level):
            extra = self.extra.copy()
            extra.update({
                'action': 'end',
                'duration_seconds': duration,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
            
            if exc_type:
                extra.update({
                    'exception': str(exc_val),
                    'exception_type': exc_type.__name__,
                    'success': False
                })
                self.logger.error(
                    f"ERROR: {self.message} (failed after {duration:.3f}s): {str(exc_val)}".format(**self.kwargs),
                    extra=extra,
                    exc_info=(exc_type, exc_val, exc_tb)
                )
            else:
                extra['success'] = True
                self.logger.log(
                    level,
                    f"END: {self.message} (took {duration:.3f}s)".format(**self.kwargs),
                    extra=extra
                )
        
        # Don't suppress exceptions
        return False
