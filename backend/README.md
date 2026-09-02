# Conduit Backend

The Django REST Framework API for Conduit, containerized and running on a legacy Django version with automated Python 3 compatibility patches.

## Table of Contents

1. [Quickstart](#quickstart)
2. [Project Goal](#project-goal)
3. [Usage](#usage)
4. [Features](#features)
5. [Environment Variables](#environment-variables)

## Quickstart

### Prerequisites

1. Install Docker.
2. Install Docker Compose.

### Steps

This service is intended to be run as part of the full stack through the root `docker-compose.yaml`. See the [root README](../README.md) for the complete setup.

To build and run only the backend in isolation for development or debugging:

1. Navigate into this folder:

```bash
   cd backend
```

2. Copy the example environment file:

```bash
   cp .env.example .env
```

3. Open `.env` and fill in your own values.
4. Build the image:

```bash
   docker build -t conduit-backend .
```

5. Run the container:

```bash
   docker run -p 8000:8000 --env-file .env conduit-backend
```

## Project Goal

This is the Django REST Framework backend for the Conduit application, a full stack social blogging platform that adheres to the [RealWorld](https://github.com/gothinkster/realworld) API spec. It exposes a JSON API for user authentication, articles, comments, profiles, and tags, backed by a PostgreSQL database.

The codebase runs on Django 1.10.5, a legacy release chosen to reflect a real world containerization scenario for older applications. Automated compatibility patches are applied during the Docker build so the application runs correctly on a modern Python version. See `patch_django.py` for details.

## Usage

The Dockerfile uses a multi stage build. The builder stage installs Python dependencies and applies the compatibility patches. The runtime stage copies only the installed packages and application code, keeping the final image small.

On container start, database migrations run automatically before the Gunicorn WSGI server starts:

```bash
python manage.py migrate --noinput && gunicorn conduit.wsgi:application --bind 0.0.0.0:8000
```

Static files, including the Django admin panel assets, are served through Whitenoise.

Configuration is handled entirely through environment variables, so no code changes are needed to adjust settings such as the allowed hosts, CORS origins, or database connection. See [Environment Variables](#environment-variables) below.

## Features

- JWT based user authentication and registration.
- Full CRUD operations for articles, including Markdown content.
- Commenting on articles.
- Favoriting articles and following other users.
- Tag based article filtering.
- Django admin panel for managing users, articles, and comments.

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `DJANGO_SECRET_KEY` | Secret key used by Django for cryptographic signing. | `a-random-secret-string` |
| `DJANGO_DEBUG` | Enables or disables Django debug mode. | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma separated list of allowed hostnames. | `localhost,127.0.0.1` |
| `DJANGO_CORS_ORIGIN_WHITELIST` | Comma separated list of origins allowed to make cross origin requests. | `localhost:8282` |
| `POSTGRES_DB` | Name of the PostgreSQL database. | `conduit` |
| `POSTGRES_USER` | PostgreSQL username. | `conduit` |
| `POSTGRES_PASSWORD` | PostgreSQL password. | `change-me` |
| `POSTGRES_HOST` | Hostname of the PostgreSQL server. | `database` |
| `POSTGRES_PORT` | Port of the PostgreSQL server. | `5432` |