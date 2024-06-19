FROM python:3.11-bookworm

WORKDIR /code

COPY poetry.lock pyproject.toml ./

RUN apt -qq update && apt -qq install -y curl

COPY ./fuelpricesgr /code/fuelpricesgr

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN POETRY_VIRTUALENVS_CREATE=false /root/.local/bin/poetry install

COPY ./var/ /code/var

RUN python -m fuelpricesgr.commands.import --verbose

CMD ["uvicorn", "fuelpricesgr.main:app", "--host", "0.0.0.0", "--port", "8000"]
