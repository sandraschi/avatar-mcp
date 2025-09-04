# Monitoring AvatarMCP with Grafana, Prometheus, Loki, and Promtail

This guide provides a complete setup for monitoring the AvatarMCP server using the Grafana observability stack.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Docker Compose Setup](#docker-compose-setup)
4. [Configuration](#configuration)
   - [Prometheus](#prometheus-configuration)
   - [Loki](#loki-configuration)
   - [Promtail](#promtail-configuration)
   - [Grafana](#grafana-configuration)
5. [AvatarMCP Integration](#avatarmcp-integration)
6. [Accessing the Dashboards](#accessing-the-dashboards)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Architecture Overview

```
+-------------+    +-------------+    +-------------+
|  AvatarMCP  |    |  Prometheus |    |    Loki     |
|  Server     |--->|  (Metrics)  |    |  (Logs)     |
+-------------+    +------+------+    +------+------+
                          |                  |
                          v                  v
                    +-----+------------------+-----+
                    |         Grafana              |
                    |  (Visualization & Alerts)    |
                    +-----------------------------+
                              |
                              v
                    +---------+----------+
                    |     Promtail       |
                    |  (Log Collection)  |
                    +--------------------+
```

## Prerequisites

- Docker and Docker Compose installed
- AvatarMCP server running (with metrics and Loki logging enabled)
- Basic understanding of monitoring concepts

## Docker Compose Setup

Create a `docker-compose.yml` file with the following services:

```yaml
version: '3.8'

services:
  # Prometheus for metrics
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    restart: unless-stopped

  # Loki for logs
  loki:
    image: grafana/loki:latest
    container_name: loki
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./loki:/etc/loki
      - loki_data:/loki
    restart: unless-stopped

  # Promtail for log collection
  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    volumes:
      - ./promtail:/etc/promtail
      - /var/log:/var/log
      - /path/to/avatarmcp/logs:/var/log/avatarmcp
    command: -config.file=/etc/promtail/promtail.yml
    restart: unless-stopped

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    depends_on:
      - prometheus
      - loki
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped

volumes:
  prometheus_data:
  loki_data:
  grafana_data:
```

## Configuration

### Prometheus Configuration

Create `prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'avatarmcp'
    static_configs:
      - targets: ['host.docker.internal:8000']  # For Docker Desktop
        # Use 'localhost:8000' for native Linux
    metrics_path: '/metrics'
    scheme: 'http'

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

### Loki Configuration

Create `loki/local-config.yaml`:

```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h
```

### Promtail Configuration

Create `promtail/promtail.yml`:

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: avatarmcp
    static_configs:
      - targets:
          - localhost
        labels:
          job: avatarmcp
          __path__: /var/log/avatarmcp/*.log
          environment: development
          service: avatarmcp
    pipeline_stages:
      - json:
          expressions:
            level:
            message:
            name:
            timestamp:
      - labels:
          level:
          name:
      - output:
          source: message
```

### Grafana Configuration

1. **Data Sources**
   - Prometheus: `http://prometheus:9090`
   - Loki: `http://loki:3100`

2. **Import Dashboard**
   - Use the dashboard JSON from `grafana/dashboards/avatarmcp-dashboard.json`

## AvatarMCP Integration

### Enabling Metrics

Start the AvatarMCP server with metrics enabled:

```bash
python -m avatarmcp.server --metrics-port 8000
```

### Enabling Loki Logging

Start the AvatarMCP server with Loki logging:

```bash
python -m avatarmcp.server --loki --loki-url http://localhost:3100/loki/api/v1/push
```

### Logging Configuration

Ensure your logging configuration in AvatarMCP includes file output:

```python
import logging
from logging.handlers import RotatingFileHandler

# Set up file handler
log_file = '/var/log/avatarmcp/avatarmcp.log'
os.makedirs(os.path.dirname(log_file), exist_ok=True)

file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

# Add handler to root logger
logging.getLogger().addHandler(file_handler)
```

## Accessing the Dashboards

1. **Grafana**: http://localhost:3000
   - Default credentials: admin/admin
   - Import the dashboard from `grafana/dashboards/avatarmcp-dashboard.json`

2. **Prometheus**: http://localhost:9090
   - For querying metrics directly

3. **Loki**: http://localhost:3100
   - For querying logs directly

## Troubleshooting

### Common Issues

1. **Prometheus cannot scrape metrics**
   - Check if the AvatarMCP server is running and accessible
   - Verify the port in `prometheus.yml` matches the `--metrics-port`
   - For Docker, use `host.docker.internal` instead of `localhost`

2. **Loki not receiving logs**
   - Check Promtail logs: `docker logs promtail`
   - Verify file permissions on log directories
   - Ensure the log path in `promtail.yml` matches where logs are written

3. **Grafana cannot connect to data sources**
   - Check if all services are running: `docker ps`
   - Verify network connectivity between containers
   - Check Grafana logs: `docker logs grafana`

## Best Practices

### Logging
- Use structured logging with JSON format
- Include relevant context in log messages
- Set appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Rotate logs to prevent disk space issues

### Metrics
- Use meaningful metric names and labels
- Avoid high cardinality labels
- Set appropriate scrape intervals
- Use histograms for request durations

### Alerting
- Set up alerts for critical metrics
- Use meaningful alert messages
- Configure notification channels
- Set appropriate alert thresholds

### Maintenance
- Monitor disk usage of Prometheus and Loki
- Set up retention policies
- Regularly update to the latest versions
- Backup important dashboards and configurations

## Advanced Configuration

### Persistent Storage
For production, configure persistent volumes for:
- Prometheus data
- Loki data
- Grafana data

### Authentication
- Enable authentication in Grafana
- Set up HTTPS for all services
- Use API tokens for service authentication

### Scaling
- For high load, consider:
  - Prometheus federation
  - Loki with S3/GCS backend
  - Horizontal pod autoscaling

## Monitoring the Monitoring Stack

Monitor the health of your monitoring stack:
- Prometheus self-monitoring
- Loki metrics endpoint
- Grafana uptime checks
- System resource usage
