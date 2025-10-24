from fastapi import APIRouter
from fastapi import Depends, HTTPException, Path
from pydantic import BaseModel, Field
from database import LocalSession
from typing import Annotated
from sqlalchemy.orm import Session
import models
from starlette import status
from .auth import get_current_user

router = APIRouter()


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency,db: db_dependency):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Authentication failed')
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get('id')).all()


@router.get("/todo-by-id/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0, description="id must be greater than 0"),
):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Authentication failed')
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def add_todo_item(user:user_dependency, db: db_dependency, todo: TodoRequest):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Authentication failed')
    try:
        todo_model = models.Todos(**todo.model_dump(), owner_id = user.get('id'))
        db.add(todo_model)
        db.commit()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to add todo")


@router.put("/todo/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,db: db_dependency, todo: TodoRequest, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Authentication failed')
    current_todo = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get('id')).first()
    if current_todo is None:
        raise HTTPException(status_code=404, detail="Todo doesnot exist")
    current_todo.title = todo.title
    current_todo.description = todo.description
    current_todo.priority = todo.priority
    current_todo.complete = todo.complete
    db.add(current_todo)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Authentication failed')
    todo_to_delete = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get('id')).first()
    if todo_to_delete is None:
        raise HTTPException(status_code=404, detail="Todo not found!")
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
