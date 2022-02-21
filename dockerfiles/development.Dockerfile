FROM code.ornl.gov:4567/rse/images/python-pyenv-tox:0.0.1

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

WORKDIR /usr/src/api
EXPOSE 8000
COPY . .

RUN poetry install

# Not using 'make run' since cannot Ctrl+C to quit the container
CMD ["poetry", "run", "uvicorn", "src.ssm_file_converter.app:app", "--host=0.0.0.0"]
