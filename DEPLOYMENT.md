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

Enable public networking for the API service. Railway supplies `PORT`; the
Docker image listens on that value and runs Alembic migrations before startup.

## Android

Replace the development URL in
`android/app/src/main/java/com/olimora/app/data/AstrologyApi.kt` with the HTTPS
domain assigned to the API, then build a fresh APK.

Do not commit `.env`, database passwords, API keys, or signing keys.

## Licensing gate

Before distributing the application or activating a public service, choose and
comply with either the Swiss Ephemeris AGPL terms or its professional license.
