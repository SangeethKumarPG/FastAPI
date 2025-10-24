from fastapi import FastAPI
from routers import auth, todos
from database import engine
import models

app = FastAPI()
app.include_router(auth.router)
app.include_router(todos.router)
models.Base.metadata.create_all(bind=engine)


