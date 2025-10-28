from posixpath import curdir
from fastapi import APIRouter
from fastapi import Depends, HTTPException, Path
from pydantic import BaseModel, Field
from database import LocalSession
from typing import Annotated
from sqlalchemy.orm import Session
import models
from starlette import status
from .auth import bcrypt_context, get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

class ChangePassword(BaseModel):
    old_password: str = Field(min_length=8, max_length=36)
    new_password: str = Field(min_length=8, max_length=36)


class UpdatePhoneNumberRequest(BaseModel):
    phone_number: str

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/me/", status_code=status.HTTP_200_OK)
async def get_my_information(user: user_dependency, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    current_user = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return current_user
    
@router.put("/change_password/", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user:user_dependency, db:db_dependency, password_change: ChangePassword):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    current_user = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not bcrypt_context.verify(password_change.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    current_user.hashed_password = bcrypt_context.hash(password_change.new_password)
    db.add(current_user)
    db.commit()
    
    
@router.put("/update_phone_number", status_code = status.HTTP_204_NO_CONTENT)
async def update_phone_number(user:user_dependency, db: db_dependency, phone_number:UpdatePhoneNumberRequest):
    current_user = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if current_user.phone_number == phone_number.phone_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already exists")
    current_user.phone_number = phone_number.phone_number
    db.add(current_user)
    db.commit()