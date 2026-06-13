# Metrics collection for the Avatar MCP server using Prometheus.
# This module provides metrics collection for monitoring the Avatar MCP server.

import logging
import time

from prometheus_client import Counter, Gauge, Histogram, Info, start_http_server


class MetricsCollector:
    # Metrics collector for the Avatar MCP server.

    def __init__(self, port: int = 8000, enabled: bool = True):
        # Initialize the metrics collector.
        # Args:
        #   port: Port to expose the Prometheus metrics on
        #   enabled: Whether metrics collection is enabled
        self.enabled = enabled
        self.port = port
        self._server_started = False

        # Check if we're in a test environment
        import sys

        is_testing = "pytest" in sys.modules or "unittest" in sys.modules

        if not self.enabled or is_testing:
            # Create dummy metrics for testing
            self.info = None
            self.requests_total = None
            self.request_duration_seconds = None
            self.avatars_loaded = None
            self.avatar_operations = None
            self.active_avatar = None
            self.chat_messages = None
            self.chat_sessions = None
            self.animation_operations = None
            self.system_uptime = None
            self.last_updated = None
            return

        try:
            self._init_metrics()
        except ValueError as e:
            if "Duplicated timeseries" not in str(e):
                raise
            logging.getLogger(__name__).debug(
                "Metrics already registered (e.g. second AvatarMCPServer), using dummy metrics"
            )
            self.info = None
            self.requests_total = None
            self.request_duration_seconds = None
            self.avatars_loaded = None
            self.avatar_operations = None
            self.active_avatar = None
            self.chat_messages = None
            self.chat_sessions = None
            self.animation_operations = None
            self.system_uptime = None
            self.last_updated = None
            return

        # Start the metrics server
        if self.enabled and not self._server_started:
            self.start_metrics_server()

    def _init_metrics(self) -> None:
        """Create Prometheus metrics. Raises ValueError if already registered."""
        # Server info
        self.info = Info("avatarmcp", "Information about the Avatar MCP server")

        # Request metrics
        self.requests_total = Counter(
            "avatarmcp_requests_total", "Total number of requests", ["method", "endpoint", "status"]
        )

        self.request_duration_seconds = Histogram(
            "avatarmcp_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint"],
            buckets=(
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
                30.0,
                60.0,
                float("inf"),
            ),
        )

        # Avatar metrics
        self.avatars_loaded = Gauge("avatarmcp_avatars_loaded", "Number of avatars currently loaded")

        self.avatar_operations = Counter(
            "avatarmcp_avatar_operations_total",
            "Total number of avatar operations",
            ["operation", "status"],
        )

        self.active_avatar = Gauge(
            "avatarmcp_active_avatar",
            "ID of the currently active avatar (0 if none)",
            ["avatar_id"],
        )

        # Chat metrics
        self.chat_messages = Counter(
            "avatarmcp_chat_messages_total",
            "Total number of chat messages processed",
            ["direction"],  # 'incoming' or 'outgoing'
        )

        self.chat_sessions = Gauge("avatarmcp_chat_sessions", "Number of active chat sessions")

        # Animation metrics
        self.animation_operations = Counter(
            "avatarmcp_animation_operations_total",
            "Total number of animation operations",
            ["operation", "status"],
        )

        # System metrics
        self.system_uptime = Gauge("avatarmcp_system_uptime_seconds", "Server uptime in seconds")

        self.last_updated = Gauge("avatarmcp_last_updated_timestamp_seconds", "Timestamp of the last metrics update")

    def start_metrics_server(self) -> None:
        # Start the Prometheus metrics server.
        if not self.enabled or self._server_started:
            return

        try:
            start_http_server(self.port)
            self._server_started = True
            logging.info("Metrics server started on port %d", self.port)
        except OSError as e:
            # 10048 = EADDRINUSE; 10013 = Windows access denied (Docker/Hyper-V port hold)
            if (
                "address already in use" in str(e).lower()
                or getattr(e, "winerror", None) in (10048, 10013)
                or e.errno in (10048, 13)
            ):
                self._server_started = True
                logging.getLogger(__name__).warning(
                    "Metrics port %d unavailable (%s); continuing without Prometheus listener",
                    self.port,
                    e,
                )
            else:
                logging.error("Failed to start metrics server: %s", e, exc_info=True)
        except Exception as e:
            logging.error("Failed to start metrics server: %s", e, exc_info=True)

    def record_request(self, method: str, endpoint: str, status: str, duration: float) -> None:
        # Record an API request.
        # Args:
        #   method: HTTP method (e.g., 'GET', 'POST')
        #   endpoint: API endpoint (e.g., '/api/avatar/load')
        #   status: Response status (e.g., 'success', 'error')
        #   duration: Request duration in seconds
        if not self.enabled or self.requests_total is None:
            return

        self.requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

    def record_avatar_operation(self, operation: str, status: str = "success") -> None:
        # Record an avatar operation.
        # Args:
        #   operation: Operation name (e.g., 'load', 'unload', 'set_active')
        #   status: Operation status ('success' or 'error')
        if not self.enabled or self.avatar_operations is None:
            return

        self.avatar_operations.labels(operation=operation, status=status).inc()

    def set_avatars_loaded(self, count: int) -> None:
        # Set the number of loaded avatars.
        # Args:
        #   count: Number of avatars currently loaded
        if not self.enabled or self.avatars_loaded is None:
            return

        self.avatars_loaded.set(count)

    def set_active_avatar(self, avatar_id: str | None) -> None:
        # Set the active avatar.
        # Args:
        #   avatar_id: ID of the active avatar, or None if no avatar is active
        if not self.enabled or self.active_avatar is None:
            return

        # Reset all active_avatar gauges
        self.active_avatar._metrics.clear()

        if avatar_id is not None:
            self.active_avatar.labels(avatar_id=avatar_id).set(1)

    def record_chat_message(self, direction: str = "incoming") -> None:
        # Record a chat message.
        # Args:
        #   direction: Message direction ('incoming' or 'outgoing')
        if not self.enabled or self.chat_messages is None:
            return

        self.chat_messages.labels(direction=direction).inc()

    def set_chat_sessions(self, count: int) -> None:
        # Set the number of active chat sessions.
        # Args:
        #   count: Number of active chat sessions
        if not self.enabled or self.chat_sessions is None:
            return

        self.chat_sessions.set(count)

    def record_animation_operation(self, operation: str, status: str = "success") -> None:
        # Record an animation operation.
        # Args:
        #   operation: Operation name (e.g., 'play', 'stop')
        #   status: Operation status ('success' or 'error')
        if not self.enabled or self.animation_operations is None:
            return

        self.animation_operations.labels(operation=operation, status=status).inc()

    def update_system_metrics(self, uptime: float) -> None:
        # Update system metrics.
        # Args:
        #   uptime: Server uptime in seconds
        if not self.enabled or self.system_uptime is None:
            return

        self.system_uptime.set(uptime)
        self.last_updated.set(time.time())
