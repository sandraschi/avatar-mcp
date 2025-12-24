"""
Loki log handler for the Avatar MCP server.

This module provides a log handler that sends logs to a Loki instance.
"""

import logging
import socket
import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class LokiLogHandler(logging.Handler):
    """Log handler that sends logs to a Loki instance."""

    def __init__(
        self,
        url: str = "http://localhost:3100/loki/api/v1/push",
        tags: dict[str, str] | None = None,
        batch_size: int = 10,
        batch_timeout: float = 5.0,
        level: int | str = logging.INFO,
        max_retries: int = 3,
        timeout: float = 5.0,
        **kwargs,
    ):
        """Initialize the Loki log handler.

        Args:
            url: Loki API endpoint URL
            tags: Additional tags to include with every log entry
            batch_size: Number of log entries to batch before sending
            batch_timeout: Maximum time to wait before sending a batch (seconds)
            level: Log level
            max_retries: Maximum number of retries for failed requests
            timeout: Request timeout in seconds
            **kwargs: Additional arguments for the parent class
        """
        super().__init__(level=level)
        self.url = url
        self.tags = tags or {}
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.timeout = timeout
        self._batch: list[dict[str, Any]] = []
        self._last_send = 0.0
        self._hostname = socket.gethostname()

        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
        )

        # Create a session with retry
        self._session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        # Set default formatter for JSON output
        self.formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to Loki."""
        try:
            # Format the log message
            message = self.format(record)

            # Create log entry in Loki format
            ns = int(record.created * 1e9)  # Convert to nanoseconds

            # Extract any extra fields from the record
            extra = {}
            if hasattr(record, "extra") and isinstance(record.extra, dict):
                extra = record.extra

            # Create labels
            labels = {
                "level": record.levelname.lower(),
                "logger": record.name,
                "host": self._hostname,
                **self.tags,
                **extra.get("labels", {}),
            }

            # Create log entry
            log_entry = {"stream": labels, "values": [[str(ns), message]]}

            self._batch.append(log_entry)

            # Check if we should send the batch
            current_time = time.time()
            if (
                len(self._batch) >= self.batch_size
                or (current_time - self._last_send) >= self.batch_timeout
            ):
                self._send_batch()

        except Exception as e:
            logger.error("Error in LokiLogHandler: %s", str(e), exc_info=True)

    def _send_batch(self) -> None:
        """Send the current batch of logs to Loki."""
        if not self._batch:
            return

        try:
            # Prepare the payload
            payload = {"streams": self._batch}

            # Send the request
            response = self._session.post(
                self.url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )

            # Check for errors
            if response.status_code != 204:
                logger.error(
                    "Failed to send logs to Loki: %d - %s", response.status_code, response.text
                )

            # Clear the batch
            self._batch = []
            self._last_send = time.time()

        except Exception as e:
            logger.error("Error sending logs to Loki: %s", str(e), exc_info=True)

    def close(self) -> None:
        """Close the handler and send any remaining logs."""
        try:
            self._send_batch()
            self._session.close()
        finally:
            super().close()

    def __del__(self) -> None:
        """Ensure resources are cleaned up."""
        self.close()
