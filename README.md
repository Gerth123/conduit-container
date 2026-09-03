# Conduit Container

A fully containerized full stack social blogging platform, built with a Django REST backend, an Angular frontend, and PostgreSQL, orchestrated through Docker Compose and deployed automatically through a GitHub Actions CI/CD pipeline.

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

The purpose of this project is to demonstrate containerizing a legacy application that was not originally built with Docker in mind, and automating its release process. The backend runs on Django 1.10.5, a version that predates several Python compatibility mechanisms, so the container build applies automated compatibility patches during the build process.

A GitHub Actions workflow builds the backend and frontend images, publishes them to the GitHub Container Registry (GHCR), and deploys the updated `docker-compose.yaml` to a remote Cloud VM over SSH. The build never happens on the target server, only prebuilt images are pulled and started there.

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

### Continuous Deployment

The `.github/workflows/deployment.yaml` workflow runs on every push to `main` (and can also be triggered manually) and consists of two jobs:

1. `build-and-push` builds the backend and frontend images and pushes them to `ghcr.io/gerth123/conduit-backend` and `ghcr.io/gerth123/conduit-frontend`. The frontend build receives `API_URL` as a build argument so the deployed frontend points to the correct backend address.
2. `deploy` copies `docker-compose.yaml` to the target VM over SCP, then opens an SSH connection and runs `docker compose pull` followed by `docker compose up -d`, so the containers are updated in detached mode without ever building on the server itself.

The workflow requires the following repository secrets to be configured under `Settings > Secrets and variables > Actions`:

| Secret | Description |
|---|---|
| `SSH_HOST` | IP address or hostname of the deployment target VM. |
| `SSH_USER` | SSH username used to connect to the VM. |
| `SSH_PRIVATE_KEY` | Private key matching a public key added to the VM's `authorized_keys`. |
| `API_URL` | Backend API URL baked into the frontend at build time, for example `http://<vm-ip>:8001/api`. |

The runtime `.env` file with database credentials and the Django secret key is kept only on the VM, in the same directory as `docker-compose.yaml`, and is never committed to the repository or passed through the workflow.

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
| `API_URL` | Backend API URL baked into the Angular frontend at build time. | `http://<vm-ip>:8001/api` |

## Known Issues

The Django backend (version 1.10.5) is a legacy release with several compatibility issues on modern Python versions. These are resolved through automated patches applied during the Docker build, documented in `backend/patch_django.py`. No application level bugs beyond what was required for containerization have been fixed.