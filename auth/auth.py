from typing import List
import jwt
import os
from fastapi import Depends,HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from database.db import get_db
from database import models
from database.schema import Token, UserCreate, UserResponse

auth_router = APIRouter()


SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """
    Creates a JWT access token for the given data.

    The token is a JSON Web Token (JWT) that contains the given data,
    with an expiration time set to the current time plus the
    ACCESS_TOKEN_EXPIRE_MINUTES environment variable.

    Args:
        data (dict): The data to encode in the token.

    Returns:
        str: The JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Returns the current user based on the token passed in the Authorization header,
    or raises a 401 Unauthorized response if the token is invalid or the user is not found.

    The token is expected to be in the format of a JWT token, signed with the SECRET_KEY.
    The payload of the token is expected to have a "sub" key with the email of the user.

    If the token is invalid or the user is not found, a 401 Unauthorized response is raised.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user: The user to register.

    Raises:
        HTTPException: If the user's email is already registered.

    Returns:
        The registered user.
    """
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@auth_router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login with username and password.
    Args:
        form_data: The username and password to use for login.
    Raises:
        HTTPException: If the email or password is incorrect.
    Returns:
        The access token and its type.
    """
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )    
    access_token = create_access_token(data={"sub": user.email})
    db.commit()
    db.refresh(user)
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post('/logout')
async def logout(user:UserResponse = Depends(get_current_user),token:Token = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    """
    Logout a user.
    This endpoint is accessible to any authenticated user. It sets the user's active status to False and returns a success message.
    Parameters:
    ----------
    user : UserResponse
        The currently authenticated user dependency.
    token : Token
        The access token dependency.
    db : Session
        The database session dependency.
    Returns:
    -------
    dict
        A message indicating the successful logout of the user.
    """
    user.is_active = False
    db.commit()
    db.refresh(user)
    return {"message": "Logout successful"}
    