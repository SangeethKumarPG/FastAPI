from fastapi import FastAPI, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from database import engine, LocalSession
from typing import Annotated, Optional
from sqlalchemy.orm import Session
import models
from starlette import status

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title:str = Field(min_length=3)
    description:str = Field(min_length=3, max_length=100)
    priority:int = Field(gt=0, lt=6)
    complete:bool

@app.get("/", status_code=status.HTTP_200_OK)
async def get_all_todos(db: db_dependency):
    return db.query(models.Todos).all()


@app.get("/todo-by-id/{todo_id}", status_code = status.HTTP_200_OK)
async def get_todo_by_id(db: db_dependency, todo_id: int = Path(gt=0, description="id must be greater than 0")):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
        
@app.post("/todo", status_code = status.HTTP_201_CREATED)
async def add_todo_item(db:db_dependency, todo:TodoRequest):
    try:
        todo_model = models.Todos(**todo.model_dump())
        db.add(todo_model)
        db.commit()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to add todo")
    
@app.put("/todo/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db:db_dependency, todo:TodoRequest, todo_id:int=Path(gt=0)):
    current_todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if current_todo is None:
        raise HTTPException(status_code=404, detail="Todo doesnot exist")
    current_todo.title = todo.title
    current_todo.description = todo.description
    current_todo.priority = todo.priority
    current_todo.complete = todo.complete
    db.add(current_todo)
    db.commit()
    
@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db:db_dependency, todo_id:int=Path(gt=0)):
    todo_to_delete = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_to_delete is None:
        raise HTTPException(status_code=404, detail='Todo not found!')
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()