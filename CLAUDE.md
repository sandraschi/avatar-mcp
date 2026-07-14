# avatar-mcp — Claude Code Guide

## Overview
FastMCP 3.4+ server for managing and animating VRM avatars — VRM import/export, bone control, facial expressions, animation, Resonite integration.

## Entry Points
- `uv run avatarmcp` → `avatarmcp.__main__:main`

## Ports
- Backend: 10793
- Frontend: 10792

## Standards
- FastMCP 3.4+ portmanteau tool pattern
- Responses: structured dicts with `success`, `message`, domain-specific fields
- Dual transport: stdio + HTTP
- See mcp-central-docs for fleet-wide standards
