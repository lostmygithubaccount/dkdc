# dkdc Architecture

## Overview

dkdc is a monorepo containing static websites, web applications, and Python packages. The architecture follows a container-first, development-focused approach with emphasis on simplicity and scalability.

## Core Components

### 1. Python Package (dkdc)
- **Location**: `src/dkdc/`
- **Dependencies**: Panel (>=1.7.0), watchfiles (>=1.0.5)
- **Purpose**: Core Python package with CLI entry point
- **Runtime**: Python 3.12+ (pinned to 3.13 in containers)

### 2. Web Applications
- **app1.py**: Panel-based data visualization app (Bokeh/NumPy sine wave demo)
- **Port**: 3007
- **Framework**: Panel with Bokeh backend

### 3. Static Websites
- **dkdc.dev**: Primary website on port 1313
- **dkdc.io**: Secondary website on port 1314
- **Generator**: Zola (v0.20.0)
- **Themes**: Terminimal (dkdc.dev), Parchment (dkdc.io)

## Container Architecture

### Base Image
- **FROM**: `ghcr.io/astral-sh/uv:debian-slim`
- **User**: `dev` (UID 1000, GID 1000) with sudo privileges
- **Shell**: zsh

### Development Tools
- **Python**: uv with multiple versions (3.11, 3.12, 3.13)
- **Node.js**: fnm with Node.js 22
- **Tools**: ruff, pytest, ranger-fm, pre-commit, ipython, pyright
- **System**: git, curl, wget, ripgrep, tmux, tree, DuckDB

### Cache Strategy
- **uv cache**: `/home/dev/.cache/uv` (persistent volume)
- **npm cache**: `/home/dev/.cache/npm` (persistent volume)
- **Environment variables**: UV_CACHE_DIR, npm_config_cache

## Docker Compose Stack

### Services Configuration
All services share:
- Same Dockerfile build
- Same user (`dev`)
- Same volume mounts (source code + caches)
- Same environment variables

#### Service Details
1. **dkdc-dev**: Zola development server for dkdc.dev
2. **dkdc-io**: Zola development server for dkdc.io  
3. **app1**: Panel application server

### Volume Strategy
- **Source code**: Bind mount `.:/app` for live reload
- **Persistent caches**: Named volumes for uv and npm caches
- **Working directories**: Service-specific paths within `/app`

## Development Container
- **devcontainer.json**: VS Code integration
- **Remote user**: `dev`
- **Workspace**: `/workspace`

## Workspace Structure
```
/app/                    # Container workspace
├── websites/           # Static sites
│   ├── dkdc.dev/      # Primary website
│   └── dkdc.io/       # Secondary website
├── apps/              # Web applications  
├── src/dkdc/          # Python package
├── packages/          # Workspace members
└── pyproject.toml     # Python project config
```

## Resilience Considerations

### Current State
- Basic container setup without restart policies
- No health checks or retry logic
- Single-container services

### Recommended Improvements
```yaml
# Add to each service in docker-compose.yaml
restart: unless-stopped
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:PORT/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Additional Resilience Options
- **Dependency management**: `depends_on` with health conditions
- **Resource limits**: memory/CPU constraints
- **Logging**: structured logging with rotation
- **Monitoring**: Prometheus metrics endpoints

## Design Philosophy

### Development = Production
- Same containers for dev and prod environments
- Consistent tooling and dependencies
- Simplified deployment pipeline

### Speed & Simplicity
- Fast startup with cached dependencies
- Minimal configuration overhead  
- Live reload for all services

### Scalability Ready
- Container-native architecture
- Stateless application design
- External cache persistence