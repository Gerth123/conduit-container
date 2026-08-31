# Conduit Frontend

## Table of Contents

1. [Quickstart](#quickstart)
2. [Project Goal](#project-goal)
3. [Usage](#usage)
4. [Features](#features)

## Quickstart

### Prerequisites

1. Install Docker.
2. Install Docker Compose.

### Steps

This service is intended to be run as part of the full stack through the root `docker-compose.yaml`. See the [root README](../README.md) for the complete setup.

To build and run only the frontend in isolation for development or debugging:

1. Navigate into this folder: `cd frontend`.
2. Build the image, pointing it to a running backend: `docker build --build-arg API_URL=http://localhost:8000/api -t conduit-frontend .`.
3. Run the container: `docker run -p 8282:80 conduit-frontend`.
4. Open the application in your browser at `http://localhost:8282`.

## Project Goal

This is the Angular frontend for the Conduit application, a full stack social blogging platform (a Medium.com clone) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API. It communicates with the Django REST backend for authentication, articles, comments, profiles, and tags.

## Usage

The Dockerfile uses a multi stage build. The builder stage installs the npm dependencies and compiles a production Angular bundle. The backend API URL is not hardcoded in the source code. Instead, it is injected at build time through the `API_URL` Docker build argument, which overwrites `src/environments/environment.prod.ts` before the build runs. This keeps the backend address out of the repository, since it can differ between local development and a deployed environment.

The runtime stage serves the compiled application through an Nginx image. A custom `nginx.conf` is included so that all unmatched routes fall back to `index.html`, which is required for Angular's client side routing to work correctly (for example, reloading the page on `/register` or `/settings` directly).

Authentication uses a JWT token, stored in the browser's local storage after login or registration. The token is attached automatically to subsequent API requests.

## Features

- User registration, login, and logout via JWT authentication.
- Article creation, editing, and deletion, with Markdown rendered client side.
- Commenting on articles, including deleting your own comments.
- Favoriting articles and following other users.
- Global feed, personalized feed (articles from followed authors), and tag based filtering, all paginated.
- Profile pages showing a user's articles or their favorited articles.
- Settings page for updating username, bio, email, password, and profile picture.