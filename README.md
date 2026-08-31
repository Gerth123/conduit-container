# Conduit Container

## Table of Contents

1. [Quickstart](#quickstart)
2. [Project Goal](#project-goal)
3. [Usage](#usage)
4. [Features](#features)
5. [Environment Variables](#environment-variables)
6. [Known Issues](#known-issues)

## Quickstart

### Prerequisites

1. Install Docker.
2. Install Docker Compose (bundled with Docker Desktop on Windows and macOS).

### Steps

1. Clone this repository.
2. Navigate into the project root folder.
3. Copy the example environment file:

```bash
   cp .env.example .env
```

4. Open `.env` and fill in your own values (see [Environment Variables](#environment-variables)).
5. Build and start all services:

```bash
   docker compose up --build -d
```

6. Open the application in your browser at `http://localhost:8282`.

## Project Goal

This repository contains a containerized version of the Conduit application, a full stack social blogging platform (a Medium.com clone) built with a Django REST backend and an Angular frontend. The application is orchestrated with Docker Compose and runs three services: a PostgreSQL database, the Django backend served through Gunicorn, and the Angular frontend served through Nginx.

The purpose of this project is to demonstrate containerizing a legacy application that was not originally built with Docker in mind. The backend runs on Django 1.10.5, a version that predates several Python compatibility mechanisms, so the container build applies automated compatibility patches during the build process.

## Usage

### Backend

The backend Dockerfile uses a multi stage build. The builder stage installs the Python dependencies and applies compatibility patches to Django's internals (see `backend/patch_django.py`) so the application runs correctly on Python 3.8. The runtime stage copies only the installed packages and application code, keeping the final image small.

On container start, the backend automatically runs database migrations before starting the Gunicorn WSGI server. Static files, including the Django admin panel assets, are served through Whitenoise rather than the Django development server.

### Frontend

The frontend Dockerfile also uses a multi stage build. The builder stage installs the npm dependencies and builds a production Angular bundle. The `API_URL` used by the frontend is injected at build time through a Docker build argument, which keeps the backend address out of the repository. The runtime stage serves the built files through an Nginx image configured to fall back to `index.html` for Angular's client side routing.

### Database

PostgreSQL data is persisted in a named Docker volume, so content survives container restarts. If you change `POSTGRES_PASSWORD` in your `.env` file after the database volume has already been created, the new password will not be picked up automatically. In that case, either reset the volume with the command below (this deletes all data) or update the password directly inside the running database.

```bash
docker compose down -v
```

### Restart behavior

All three services are configured with `restart: unless-stopped`. If the main process inside a container is terminated unexpectedly, Docker restarts the container automatically.

### Logs

View logs for a running service:

```bash
docker compose logs backend
```

Save logs to a file for later use:

```bash
docker compose logs backend > backend-logs.txt
```

## Features

- User registration and login secured with JWT authentication.
- Article creation, editing, and deletion, including a Markdown enabled editor.
- Commenting on articles.
- Favoriting articles and following other users.
- Tag based article filtering.
- A global feed and a personalized feed based on followed authors.
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
| `API_URL` | Backend API URL baked into the Angular frontend at build time. | `http://localhost:8000/api` |

## Known Issues

The Django backend (version 1.10.5) is a legacy release with several compatibility issues on modern Python versions. These are resolved through automated patches applied during the Docker build, documented in `backend/patch_django.py`. No application level bugs beyond what was required for containerization have been fixed.