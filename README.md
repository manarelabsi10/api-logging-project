# API Logging Project

A learning project demonstrating a FastAPI application with input validation, structured rotating file logs, and Docker deployment.

## Features

- `GET /health` health check endpoint.
- `POST /items` creates an item and returns its ID.
- `PUT /items/{item_id}` updates an existing item.
- `DELETE /items/{item_id}` deletes an existing item.
- Request validation with Pydantic.
- Validation failures are returned as HTTP `422` responses and recorded as `WARNING` logs.
- Successful item operations are recorded in a rotating log file.
- Docker image built with Python and dependencies managed by `uv`.

> Items are stored in application memory for learning purposes. They are cleared when the application restarts.

## Project Structure

```text
api-logging-project/
├── .dockerignore
├── .gitignore
├── .python-version
├── Dockerfile
├── README.md
├── pyproject.toml
├── uv.lock
├── logs/
│   └── app.log
└── src/
    └── api_logging_project/
        ├── __init__.py
        ├── logging_config.py
        └── main.py
```

- `src/api_logging_project/main.py` defines the FastAPI app, endpoints, input model, and validation error handler.
- `src/api_logging_project/logging_config.py` configures the application logger and rotating log file.
- `pyproject.toml` defines the project and its dependencies.
- `uv.lock` records the exact dependency versions used by `uv`.
- `Dockerfile` describes how to build and run the app inside a Docker image.
- `.dockerignore` lists files that Docker should leave out of the build.
- `.gitignore` lists generated and local files that Git should not track.
- `.python-version` records the Python version selected for the project.
- `logs/app.log` is generated at runtime. It is kept in the project folder and is not included in the Docker image.

## Logging

The application writes logs to `logs/app.log` using UTF-8 encoding. Log entries include the timestamp, level, logger name, and message. The rotating file handler starts a new log file when the current file reaches approximately 1 MB and keeps up to three backup files.

Examples of logged events include successful item creation, updates, deletions, health checks, and request validation failures.

## Run with Docker

Run these commands in PowerShell from the project folder.

Build the image:

```powershell
docker build -t api-logging-project .
```

Start the container and mount the project's `logs` folder so that logs appear on the host:

```powershell
docker run -d --name api-logging-container -p 127.0.0.1:8000:8000 --mount "type=bind,source=$($PWD.Path)\logs,target=/app/logs" api-logging-project:latest
```

Check that the container is running:

```powershell
docker ps
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Stop and remove the container:

```powershell
docker stop api-logging-container
docker rm api-logging-container
```

Stopping and removing the container does not remove `logs/app.log` from the project folder because the log folder is mounted from the host.

## Test the API in Swagger

Open `http://127.0.0.1:8000/docs`.

### Create an item

Use `POST /items` with this JSON body:

```json
{
  "name": "Notebook",
  "price": 25.5,
  "quantity": 10
}
```

A successful response has HTTP status `201`. It includes the new item's `id`; use that ID in the update and delete requests.

### Update an item

Use `PUT /items/{item_id}`. Enter the ID returned by `POST /items` and provide a complete item body:

```json
{
  "name": "Updated Notebook",
  "price": 30,
  "quantity": 8
}
```

A successful response confirms the updated item. An unknown ID returns HTTP `404`.

### Delete an item

Use `DELETE /items/{item_id}` with an existing item's ID. A successful response confirms deletion. An unknown ID returns HTTP `404`.

### Check validation errors

Try `POST /items` with an invalid body, for example:

```json
{
  "name": "",
  "price": 15000,
  "quantity": 5
}
```

The empty name violates the minimum length rule, so the API returns HTTP `422`. The validation failure is also recorded as a `WARNING` in `logs/app.log`.

The item fields have these rules:

- `name`: 1 to 50 characters.
- `price`: greater than zero.
- `quantity`: zero or greater.

## View the log file

After making API requests, open `logs/app.log` in the project folder. It contains the application's recorded events.