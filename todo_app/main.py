from fastapi import FastAPI
from routers import auth, todos, admin, user
from database import engine
import models

app = FastAPI()
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)
models.Base.metadata.create_all(bind=engine)


