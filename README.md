# API Logging Project

A learning project demonstrating a FastAPI application with input validation, structured rotating file logs, PostgreSQL persistence, and Docker.

## Features

- `GET /health` health check endpoint.
- `GET /items` returns all items stored in PostgreSQL.
- `GET /items` caches its PostgreSQL results in Redis for 60 seconds.
- `POST /items` creates an item in PostgreSQL and returns its ID.
- `PUT /items/{item_id}` updates an item in PostgreSQL.
- `DELETE /items/{item_id}` deletes an item from PostgreSQL.
- Request validation with Pydantic.
- Validation failures return HTTP `422` responses and are recorded as `WARNING` logs.
- Item changes and health checks are recorded in a rotating log file.
- PostgreSQL runs in a Docker container with a named volume for persistent data.
- Python dependencies are managed by `uv`.
- Item create, update, and delete operations invalidate the items cache.
- Redis runs in a Docker container.

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
├── sql/
│   └── schema.sql
├── logs/
│   └── app.log
└── src/
    └── api_logging_project/
        ├── __init__.py
        ├── database.py
        ├── cache.py
        ├── logging_config.py
        └── main.py
```

- `src/api_logging_project/main.py` defines the FastAPI app, endpoints, input model, and validation error handler.
- `src/api_logging_project/database.py` creates PostgreSQL connections using the `DATABASE_URL` environment variable.
- `src/api_logging_project/logging_config.py` configures the application logger and rotating log file.
- `src/api_logging_project/cache.py` connects to Redis and caches the items list for 60 seconds.
- `sql/schema.sql` defines the PostgreSQL `items` table.
- `pyproject.toml` defines the project and its dependencies.
- `uv.lock` records the exact dependency versions used by `uv`.
- `Dockerfile` describes how to build the application image.
- `.dockerignore` lists files Docker should leave out of the image.
- `.gitignore` lists generated and local files Git should not track.
- `logs/app.log` is generated at runtime and is not included in the Docker image.

## Run the API with PostgreSQL

In this development setup, PostgreSQL runs in Docker and the FastAPI application runs locally from PowerShell.

Run the following commands from the project folder.

### Start PostgreSQL

Download the PostgreSQL image:

```powershell
docker pull postgres:17
```

Create and start the PostgreSQL container:

```powershell
docker run --name postgres-db -e POSTGRES_USER=app_user -e POSTGRES_PASSWORD=dev_password_change_me -e POSTGRES_DB=api_logging -p 127.0.0.1:5432:5432 -v pgdata:/var/lib/postgresql/data -d postgres:17
```

The `pgdata` Docker volume keeps database data when the container is stopped. The example password is for local development. Use the same password in the `DATABASE_URL` below.

If you already created the container, start it with:

```powershell
docker start postgres-db
```

Check that the container is running:

```powershell
docker ps --filter name=postgres-db
```

### Create the database table

Apply the schema from the project folder:

```powershell
Get-Content .\sql\schema.sql | docker exec -i postgres-db psql -U app_user -d api_logging
```

The schema creates an `items` table with an automatically generated ID, a name, a positive price with two decimal places, and a non-negative quantity.

### Configure the API connection

Set the connection string in the same PowerShell window that you will use to run the API:

```powershell
$env:DATABASE_URL = "postgresql://app_user:dev_password_change_me@localhost:5432/api_logging"
```

If you open a new PowerShell window, set `DATABASE_URL` again in that window.

Install the project dependencies:

```powershell
uv sync
```

Start the API:

```powershell
uv run uvicorn api_logging_project.main:app --reload
```

Keep this PowerShell window open while using the API.

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Test the API in Swagger

Open `http://127.0.0.1:8000/docs`.

### Create an item

Use `POST /items` with this JSON body:

```json
{
  "name": "Notebook",
  "price": 25.50,
  "quantity": 10
}
```

A successful response has HTTP status `201` and includes the new item's ID.

### Read items

Use `GET /items` to read all items stored in PostgreSQL. The item created by `POST /items` should appear in the response.

### Update an item

Use `PUT /items/{item_id}`. Enter the ID returned by `POST /items` and provide a complete item body:

```json
{
  "name": "Updated Notebook",
  "price": 30.00,
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
  "price": 0,
  "quantity": -1
}
```

The API returns HTTP `422` when a value fails validation. The rules are:

- `name`: 1 to 50 characters.
- `price`: greater than zero, with at most two decimal places.
- `quantity`: zero or greater.

Validation failures are also recorded as `WARNING` entries in `logs/app.log`.

## Verify data directly in PostgreSQL

Connect to the database container:

```powershell
docker exec -it postgres-db psql -U app_user -d api_logging
```

List the stored items:

```sql
SELECT * FROM items;
```

Exit `psql`:

```text
\q
```

### Start Redis

Download the Redis image:

```powershell
docker pull redis
```

Create the container the first time:

```powershell
docker run -d --name redis-cache -p 127.0.0.1:6379:6379 redis
```

If the container already exists, start it with:

```powershell
docker start redis-cache
```

### Configure the Redis connection

Set the connection URL in the same PowerShell window used to start the API:

```powershell
$env:REDIS_URL = "redis://localhost:6379/0"
```

`GET /items` reads from Redis when the cached list exists. On a cache miss, it reads from PostgreSQL and caches the list for 60 seconds. Creating, updating, or deleting an item clears the cached list.

To inspect the cached list directly:

```powershell
docker exec -it redis-cache redis-cli GET items:all
```

### Run the API in Docker

The PostgreSQL and Redis containers must be running.

Create a shared network and attach both containers once:

```powershell
docker network create api-logging-network
docker network connect api-logging-network postgres-db
docker network connect api-logging-network redis-cache
```

Build the API image:

```powershell
docker build -t api-logging-project:redis .
```

On first setup, create `.env` from the example and replace `YOUR_POSTGRES_PASSWORD` with the PostgreSQL password:

```powershell
Copy-Item .env.example .env
```

Run the API container:

```powershell
docker run -d --name api-logging-api --network api-logging-network --env-file .env -p 127.0.0.1:8000:8000 api-logging-project:redis
```

Check that the containers are running:

```powershell
docker ps
```

Open Swagger UI at `http://127.0.0.1:8000/docs`.

Inspect the cached items in Redis:

```powershell
docker exec -it redis-cache redis-cli GET items:all
```

## View the log file

After making API requests, open `logs/app.log` in the project folder. It contains the application's recorded events.

## Stop the services

Stop the API with `Ctrl+C` in the PowerShell window running Uvicorn.

Stop PostgreSQL while keeping its data:

```powershell
docker stop postgres-db
docker stop redis-cache
docker stop api-logging-api
```


Start PostgreSQL again later with:

```powershell
docker start postgres-db
docker start redis-cache
```