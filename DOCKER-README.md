# AvatarMCP Docker Setup

This guide explains how to set up and run the AvatarMCP server using Docker Compose.

## Prerequisites

- Docker Engine 19.03.0+
- Docker Compose 1.29.0+
- Git (for cloning the repository)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/avatarmcp.git
   cd avatarmcp
   ```

2. Create a `models` directory and add your VRM files:
   ```bash
   mkdir -p models
   # Copy your VRM files to the models directory
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Access the services:
   - MCP Server: http://localhost:8000
   - Metrics: http://localhost:8001
   - Grafana: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090

## Configuration

### Environment Variables

You can configure the MCP server using these environment variables in `docker-compose.yml`:

- `MCP_HOST`: Host to bind the server to (default: 0.0.0.0)
- `MCP_PORT`: Port to listen on (default: 8000)
- `METRICS_PORT`: Port for metrics server (default: 8001)
- `LOKI_ENABLED`: Enable Loki logging (default: false)
- `LOKI_URL`: URL for Loki logging server

### Volumes

- `./models:/app/models`: Mount VRM models here
- `./logs:/app/logs`: Logs directory

## Monitoring Stack

The Docker Compose file includes a complete monitoring stack:

- **Prometheus**: For metrics collection
- **Loki**: For log aggregation
- **Promtail**: For log collection
- **Grafana**: For visualization

## Building the Image

To rebuild the Docker image:

```bash
docker-compose build
```

## Stopping the Services

To stop all services:

```bash
docker-compose down
```

## Troubleshooting

### View Logs

View logs for all services:

```bash
docker-compose logs -f
```

View logs for a specific service:

```bash
docker-compose logs -f avatarmcp
```

### Clean Up

To remove all containers, networks, and volumes:

```bash
docker-compose down -v
```

## License

[Your License Here]
