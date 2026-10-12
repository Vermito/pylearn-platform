FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1

WORKDIR /app

RUN pip install --no-cache-dir "poetry>=2,<3"

COPY pyproject.toml poetry.lock ./

RUN poetry install \
    --only main \
    --no-root \
    --no-ansi

COPY . .

RUN useradd \
    --create-home \
    --uid 10001 \
    appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]