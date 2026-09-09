"""Entrypoint for starting the Proyecto Micelio SaaS server."""

import uvicorn
from micelio.api.app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("micelio.main:app", host="0.0.0.0", port=8000, reload=True)
