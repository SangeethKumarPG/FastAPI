from fastapi import APIRouter
from fastapi import Depends, HTTPException, Path
from pydantic import BaseModel, Field
from database import LocalSession
from typing import Annotated
from sqlalchemy.orm import Session
import models
from starlette import status
from .auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency, db:db_dependency):
    if user is None or user.get('role')!='admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return db.query(models.Todos).all()
    
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency, db:db_dependency, todo_id:int = Path(gt=0)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='not authorized')
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()