FROM python:3.11-alpine

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=true

RUN pip install poetry

COPY pyproject.toml poetry.lock ./alembic.ini /app/
WORKDIR /app
EXPOSE 8000

RUN poetry install
RUN /app/.venv/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        fastapi-user

ENV PATH="/app/.venv/bin:$PATH"
USER fastapi-user
