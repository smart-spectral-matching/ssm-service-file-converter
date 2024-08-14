FROM python:3.8 AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PDM_VERSION=2.7.4 \
    PDM_HOME=/usr/local

RUN apt update \
    && apt install -y curl make \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python -

# Production
WORKDIR /usr/src/api
EXPOSE 8000
COPY . .
RUN pdm install --no-lock --prod
CMD ["/usr/src/api/.venv/bin/uvicorn", "src.ssm_file_converter.app:app", "--host=0.0.0.0"]

# Development
FROM production AS development
RUN pdm install --no-lock -G:all
CMD ["pdm", "run", "uvicorn", "src.ssm_file_converter.app:app", "--host=0.0.0.0"]
