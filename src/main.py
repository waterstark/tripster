from fastapi import FastAPI

from src.auth.routers import auth_router
from src.publication.routers import publication_router


app = FastAPI(title="App")

app.include_router(auth_router)
app.include_router(publication_router)
