# Fuel Prices

The purpose of this project is to create a database of fuel prices in Greece. Daily and weekly data about fuel prices
are regularly uploaded at the [Παρατηρητήριο Τιμών Υγρών Καυσίμων](http://www.fuelprices.gr) website by the Greek
Government, but the data are published as PDF files. In order to process the data more easily, this project fetches
those PDF files, extracts the data from them, inserts them in a database, and exposes them in an API.

Data are available since:

* 2012-04-27 for weekly country data
* 2012-05-04 for weekly prefecture data
* 2017-08-28 for daily country data
* 2017-03-14 for daily prefecture data

## Running the API

The backend API is a [Python](https://www.python.org) based project, built with [FastAPI](https://fastapi.tiangolo.com),
that uses [Poetry](https://python-poetry.org) for dependency management. In order to install the dependencies, you need
to run:

```
poetry install
```

The data are stored in an [SQLite](https://www.sqlite.org) database. In order to fetch the data you need to run:

```
python -m fuelpricesgr.commands.import
```

This command accepts various parameters to limit the data to be fetched. You can see them by running

```
python -m fuelpricesgr.commands.import --help
```

Now you can launch the API by running the command:

```
uvicorn fuelpricesgr.main:app
```

The API is now available at http://localhost:8000. The documentation for the API is available at
http://localhost:8000/docs.


## Running with docker

In order to build the Docker image run

```
docker build -t mavroprovato/fuelpricesgr .
```

In order to run the docker image run

```
docker run -p 8000:8000 mavroprovato/fuelpricesgr
```