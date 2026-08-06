# Olimora test deployment

This configuration is intended for a small, trusted testing group.

## Railway services

Create two services in one Railway project:

1. A PostgreSQL database.
2. The Olimora API built from the repository Dockerfile.

Set these variables on the API service:

```text
DATABASE_URL=${{Postgres.DATABASE_URL}}
APP_ENV=production
LOG_LEVEL=INFO
EPHEMERIS_PATH=/app/ephe
APP_VERSION=0.1.0
```

The testing API is available at:

```text
https://olimora-production.up.railway.app
```

Railway supplies `PORT`; the Docker image listens on that value and runs
Alembic migrations before startup.

## Android

The Android test build uses the Railway HTTPS domain above. A local-only build
may temporarily point the same constants to `http://127.0.0.1:8000`.

Do not commit `.env`, database passwords, API keys, or signing keys.

## Licensing gate

Before distributing the application or activating a public service, choose and
comply with either the Swiss Ephemeris AGPL terms or its professional license.
