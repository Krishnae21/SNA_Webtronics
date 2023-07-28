from fastapi import FastAPI, Header
from src.auth.auth import router as auth_router
from src.posts.posts import router as post_router
from typing import Annotated
from fastapi.openapi.utils import get_openapi
import uvicorn

app = FastAPI(title="Social Networking Application", debug=True)

app.include_router(auth_router)
app.include_router(post_router)

if __name__ == "__main__":
    uvicorn.run(app)
