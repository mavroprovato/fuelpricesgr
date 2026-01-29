#!/usr/bin/env bash

# Start server
uv run uvicorn fuelpricesgr.main:app --host 0.0.0.0 --port 8000
