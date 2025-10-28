from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import LocalSession
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError



SECRET_KEY = '6bbcc4d4f914e41066d264ec59e8eb4665776127796fa772023d46741a049251'
ALGORITHM = 'HS256'
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token/")

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str
    
class Token(BaseModel):
    access_token:str
    token_type:str


def authenticate_user(username:str, password:str, db):
    user = db.query(Users).filter(Users.user_name == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user
    
def create_access_token(username:str, user_id:int,role:str, expires_delta:timedelta):
    encode = {'sub':username, 'id':user_id,'role':role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name:str = payload.get('sub')
        user_id:int = payload.get('id')
        user_role:str = payload.get('role')
        if user_id is None or user_name is None or user_role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
        return {"username":user_name, "id":user_id,"role":user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

        

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUserRequest, db:db_dependency):
    create_user_model = Users(
        email = user.email,
        user_name = user.username,
        first_name = user.first_name,
        last_name = user.last_name,
        hashed_password = bcrypt_context.hash(user.password),
        role = user.role,
        is_active = True,
        phone_number = user.phone_number,
    )
    db.add(create_user_model)
    db.commit()
    

@router.post("/token/", response_model=Token)
async def login_for_refresh_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db:db_dependency):
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Failed to authenticate user')
        token_str = create_access_token(username=user.user_name, user_id=user.id,role=user.role, expires_delta=timedelta(minutes=20))
        return{
            "access_token":token_str,
            "token_type":"bearer"
        }
    
