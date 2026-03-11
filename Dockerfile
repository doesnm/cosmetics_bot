FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --frozen

COPY alembic.ini ./
COPY migrations/ ./migrations/
COPY src/ ./src/
COPY scripts/ ./scripts/

CMD ["uv", "run", "python", "-m", "src"]
