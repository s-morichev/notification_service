import uvicorn

from src.api.v1 import publish
from src.config import app

app.include_router(publish.router, prefix="/api/v1", tags=["Publish"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
