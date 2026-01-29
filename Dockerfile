FROM python:3.13-slim-trixie

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin/:$PATH"

# Install OS dependencies
RUN apt-get -qq update && \
    apt-get -qqy install curl ca-certificates pkg-config build-essential libpq-dev default-libmysqlclient-dev

# Download the latest uv installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the uv installer then remove it
RUN sh /uv-installer.sh -q && rm /uv-installer.sh

# Create the app directory
RUN mkdir /app

# Set the working directory
WORKDIR /app

# Copy the files required to install dependencies
COPY pyproject.toml uv.lock /app/

# Copy the Django project to the container
COPY . /app/

# Install python dependencies
RUN uv sync -q --locked

# Run Django's development server
ENTRYPOINT ["/bin/bash", "/app/docker-entrypoint.sh"]
