FROM python:3.8 as production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.2.0
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Production
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create false

WORKDIR /usr/src/api
EXPOSE 8000
COPY . .

RUN poetry install --no-dev
CMD ["uvicorn", "src.ssm_file_converter.app:app", "--host=0.0.0.0"]

# Development
FROM production as development
RUN poetry install
CMD ["poetry", "run", "uvicorn", "src.ssm_file_converter.app:app", "--host=0.0.0.0"]
