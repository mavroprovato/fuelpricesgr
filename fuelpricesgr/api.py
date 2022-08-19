"""The FastAPI main module
"""
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def index():
    """Returns the status of the application.
    """
    return {"status": "OK"}
