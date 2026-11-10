FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /uvx /bin/

WORKDIR /app

ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --locked --no-install-project

COPY src ./src

RUN uv sync --locked --no-editable

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "api_logging_project.main:app", "--host", "0.0.0.0", "--port", "8000"]