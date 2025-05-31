# dkdc

***The monorepo for me.***

## Quick Start

```bash
# Development (direct port access)
./bin/up.sh

# Production (nginx routing + SSL)
./bin/up.sh -e prod

# VPS deployment
curl -sSL https://raw.githubusercontent.com/lostmygithubaccount/dkdc/main/bin/deploy.sh | bash
```

## What's Inside

- **dkdc.dev**: Primary website (Zola)
- **dkdc.io**: Secondary website (Zola) 
- **app.dkdc.io**: Panel data visualization app
- **PostgreSQL**: Data catalog for DuckDB

## Development URLs

- http://localhost:1313 (dkdc.dev)
- http://localhost:1314 (dkdc.io)
- http://localhost:3007 (app.dkdc.io)

## Production URLs

- https://dkdc.dev
- https://dkdc.io
- https://app.dkdc.io

## Key Commands

```bash
# Start all services
./bin/up.sh

# View logs
docker compose logs -f

# Stop everything
docker compose down

# Rebuild containers
./bin/up.sh --build

# Production deployment
./bin/deploy.sh

# SSL setup
./bin/ssl-setup.sh
```

