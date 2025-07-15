from fastapi import FastAPI
from app.database import Base, engine
from app.routers import document_routes



app = FastAPI(title="Document API")
app.include_router(document_routes.router)
