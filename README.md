# Fuel Prices

The purpose of this project is to create a database of fuel prices in Greece. Daily and weekly data about fuel prices
are regularly uploaded at the [Παρατηρητήριο Τιμών Υγρών Καυσίμων](http://www.fuelprices.gr/) website by the Greek
Government, but the data are published as PDF files. In order to process the data more easily, this project fetches
those PDF files, extracts the data from them, inserts them in a database, and exposes them in an API.

## Installation

This is a Python based project that uses Poetry in order to manage its dependencies. In order to install its
dependencies, you need to run

```
poetry install
```

The data are stored in a SQLite database. In order to fetch them run

```
python -m fuelpricesgr.fetch
```

This command accepts various parameters to limit the data to be fetched. You can see them by running
`python -m fuelpricesgr.fetch --help`

Now you can launch the API by running the command:

```
uvicorn fuelpricesgr.api:app
```

The API is now available at http://localhost:8000. The documentation of the API is available at
http://localhost:8000/docs.

A simple fronted for the API is available in the `frontend` directory.
