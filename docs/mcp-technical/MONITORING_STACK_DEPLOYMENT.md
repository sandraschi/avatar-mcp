# 📊 Monitoring Stack Deployment Guide

**Production monitoring and observability for MCP servers**

---

## 🎯 **Monitoring Strategy Overview**

### **What to Monitor**

- ✅ **Application Health** - Server status, tool execution
- ✅ **Performance Metrics** - Response times, throughput
- ✅ **Error Tracking** - Exceptions, failures, crashes
- ✅ **Resource Usage** - CPU, memory, disk
- ✅ **Business Metrics** - Tool usage, user activity

### **Monitoring Stack Components**

- ✅ **Logging** - Structured logs with context
- ✅ **Metrics** - Performance and business metrics
- ✅ **Alerting** - Proactive issue detection
- ✅ **Dashboards** - Visual monitoring and analysis
- ✅ **Tracing** - Request flow analysis

---

## 🔧 **Logging Infrastructure**

### **Structured Logging Setup**

```python
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

# Setup logging
def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup structured logging for the application."""
    
    logger = logging.getLogger("mcp_server")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add stderr handler for Claude Desktop compatibility
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(StructuredFormatter())
    logger.addHandler(stderr_handler)
    
    # Add file handler for persistent logs
    file_handler = logging.FileHandler("mcp_server.log")
    file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(file_handler)
    
    return logger

# Usage in your MCP server
logger = setup_logging("DEBUG")

@app.tool()
async def my_tool(param: str) -> Dict[str, Any]:
    """Tool with comprehensive logging."""
    logger.info("Tool execution started", extra={
        "extra_fields": {
            "tool_name": "my_tool",
            "param": param,
            "user_id": "anonymous"
        }
    })
    
    try:
        result = await some_operation(param)
        
        logger.info("Tool execution completed", extra={
            "extra_fields": {
                "tool_name": "my_tool",
                "result_status": "success",
                "execution_time_ms": 150
            }
        })
        
        return {"status": "success", "result": result}
        
    except Exception as e:
        logger.error("Tool execution failed", extra={
            "extra_fields": {
                "tool_name": "my_tool",
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        }, exc_info=True)
        
        return {"status": "error", "message": str(e)}
```

### **Log Aggregation with ELK Stack**

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  elasticsearch:
    image: elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: logstash:8.8.0
    ports:
      - "5044:5044"
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:8.8.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

### **Logstash Configuration**

```ruby
# logstash.conf
input {
  file {
    path => "/var/log/mcp_server.log"
    start_position => "beginning"
    codec => "json"
  }
}

filter {
  if [message] {
    mutate {
      add_field => { "service" => "mcp_server" }
    }
  }
  
  if [extra_fields] {
    ruby {
      code => "
        extra_fields = event.get('extra_fields')
        if extra_fields.is_a?(Hash)
          extra_fields.each do |key, value|
            event.set(key, value)
          end
        end
      "
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "mcp-server-logs-%{+YYYY.MM.dd}"
  }
}
```

---

## 📈 **Metrics Collection**

### **Application Metrics**

```python
import time
from typing import Dict, Any
from dataclasses import dataclass
from collections import defaultdict, Counter

@dataclass
class Metrics:
    """Application metrics collector."""
    
    # Performance metrics
    request_count: int = 0
    request_duration_ms: float = 0.0
    error_count: int = 0
    
    # Tool-specific metrics
    tool_executions: Dict[str, int] = None
    tool_durations: Dict[str, float] = None
    tool_errors: Dict[str, int] = None
    
    def __post_init__(self):
        if self.tool_executions is None:
            self.tool_executions = defaultdict(int)
        if self.tool_durations is None:
            self.tool_durations = defaultdict(float)
        if self.tool_errors is None:
            self.tool_errors = defaultdict(int)

# Global metrics instance
metrics = Metrics()

def track_tool_execution(tool_name: str):
    """Decorator to track tool execution metrics."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            metrics.request_count += 1
            metrics.tool_executions[tool_name] += 1
            
            try:
                result = await func(*args, **kwargs)
                
                # Track success
                duration_ms = (time.time() - start_time) * 1000
                metrics.request_duration_ms += duration_ms
                metrics.tool_durations[tool_name] += duration_ms
                
                return result
                
            except Exception as e:
                # Track error
                metrics.error_count += 1
                metrics.tool_errors[tool_name] += 1
                raise
                
        return wrapper
    return decorator

# Usage in your MCP server
@app.tool()
@track_tool_execution("my_tool")
async def my_tool(param: str) -> Dict[str, Any]:
    """Tool with automatic metrics tracking."""
    # Your tool logic here
    return {"result": "success"}
```

### **Prometheus Metrics Export**

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Define metrics
REQUEST_COUNT = Counter('mcp_requests_total', 'Total requests', ['tool_name'])
REQUEST_DURATION = Histogram('mcp_request_duration_seconds', 'Request duration', ['tool_name'])
ERROR_COUNT = Counter('mcp_errors_total', 'Total errors', ['tool_name', 'error_type'])
ACTIVE_CONNECTIONS = Gauge('mcp_active_connections', 'Active connections')

def setup_prometheus_metrics(port: int = 8000):
    """Setup Prometheus metrics server."""
    start_http_server(port)
    logger.info(f"Prometheus metrics server started on port {port}")

# Enhanced metrics tracking
def track_prometheus_metrics(tool_name: str):
    """Decorator for Prometheus metrics."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Track success metrics
                REQUEST_COUNT.labels(tool_name=tool_name).inc()
                REQUEST_DURATION.labels(tool_name=tool_name).observe(time.time() - start_time)
                
                return result
                
            except Exception as e:
                # Track error metrics
                ERROR_COUNT.labels(tool_name=tool_name, error_type=type(e).__name__).inc()
                raise
                
        return wrapper
    return decorator
```

---

## 🚨 **Alerting System**

### **Alert Rules Configuration**

```yaml
# alerting-rules.yml
groups:
  - name: mcp_server_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(mcp_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(mcp_request_duration_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response times detected"
          description: "95th percentile response time is {{ $value }} seconds"

      - alert: ServerDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "MCP server is down"
          description: "Server has been down for more than 1 minute"
```

### **Alertmanager Configuration**

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@yourcompany.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://localhost:5001/webhook'
        send_resolved: true

  - name: 'email'
    email_configs:
      - to: 'admin@yourcompany.com'
        subject: 'MCP Server Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
```

---

## 📊 **Dashboard Configuration**

### **Grafana Dashboard**

```json
{
  "dashboard": {
    "title": "MCP Server Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(mcp_requests_total[5m])",
            "legendFormat": "{{tool_name}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(mcp_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(mcp_errors_total[5m])",
            "legendFormat": "{{tool_name}} - {{error_type}}"
          }
        ]
      }
    ]
  }
}
```

### **Kibana Dashboard**

```json
{
  "title": "MCP Server Logs",
  "panels": [
    {
      "title": "Log Volume Over Time",
      "type": "histogram",
      "query": "*",
      "timeField": "timestamp"
    },
    {
      "title": "Error Distribution",
      "type": "pie",
      "query": "level:ERROR",
      "groupBy": "error_type"
    },
    {
      "title": "Tool Usage",
      "type": "bar",
      "query": "*",
      "groupBy": "tool_name"
    }
  ]
}
```

---

## 🔍 **Distributed Tracing**

### **OpenTelemetry Integration**

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

def setup_tracing():
    """Setup distributed tracing."""
    
    # Create tracer provider
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    
    # Create Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )
    
    # Create span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    return tracer

# Usage in your MCP server
tracer = setup_tracing()

@app.tool()
async def my_tool(param: str) -> Dict[str, Any]:
    """Tool with distributed tracing."""
    with tracer.start_as_current_span("my_tool_execution") as span:
        span.set_attribute("tool_name", "my_tool")
        span.set_attribute("param", param)
        
        try:
            result = await some_operation(param)
            span.set_attribute("result_status", "success")
            return {"result": result}
            
        except Exception as e:
            span.set_attribute("result_status", "error")
            span.set_attribute("error_message", str(e))
            span.record_exception(e)
            raise
```

---

## 🚀 **Deployment Strategies**

### **Development Environment**

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  mcp-server:
    build: .
    volumes:
      - .:/app
    environment:
      - LOG_LEVEL=DEBUG
      - METRICS_ENABLED=true
    depends_on:
      - prometheus
      - grafana

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

### **Production Environment**

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  mcp-server:
    image: your-mcp-server:latest
    environment:
      - LOG_LEVEL=INFO
      - METRICS_ENABLED=true
    restart: unless-stopped
    depends_on:
      - prometheus
      - alertmanager

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alerting-rules.yml:/etc/prometheus/alerting-rules.yml
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana-dashboards:/var/lib/grafana/dashboards
    restart: unless-stopped
```

---

## 📋 **Monitoring Checklist**

### **Setup Checklist**

- [ ] **Structured logging** implemented
- [ ] **Metrics collection** configured
- [ ] **Alert rules** defined
- [ ] **Dashboards** created
- [ ] **Log aggregation** setup
- [ ] **Error tracking** enabled
- [ ] **Performance monitoring** active
- [ ] **Health checks** implemented

### **Operational Checklist**

- [ ] **Log retention** policy defined
- [ ] **Alert channels** configured
- [ ] **Escalation procedures** documented
- [ ] **Dashboard access** granted
- [ ] **Metrics storage** capacity planned
- [ ] **Backup procedures** for monitoring data
- [ ] **Security** for monitoring endpoints
- [ ] **Documentation** for monitoring setup

---

## 🎯 **Best Practices**

### **1. Start Simple**

- Begin with basic logging
- Add metrics gradually
- Implement alerts for critical issues first
- Expand monitoring as needed

### **2. Focus on Business Value**

- Monitor what matters to users
- Track business metrics, not just technical metrics
- Set up alerts for user-facing issues
- Measure success, not just failures

### **3. Keep It Maintainable**

- Use standard tools and formats
- Document monitoring setup
- Automate monitoring deployment
- Regular review and cleanup

### **4. Security Considerations**

- Secure monitoring endpoints
- Encrypt sensitive data in logs
- Control access to dashboards
- Audit monitoring access

**Remember**: Good monitoring helps you understand your system and respond to issues quickly. Start simple and grow your monitoring capabilities over time. 📊✨