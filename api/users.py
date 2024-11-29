from calendar import c
from turtle import up
from typing import List
from fastapi import APIRouter,Depends,HTTPException,status
from database import models
from sqlalchemy.orm import Session
from database.db import get_db
from database.schema import UpdateUser, UserResponse
from auth.auth import get_current_user, get_password_hash

user_router = APIRouter()

@user_router.get('/users',response_model=List[UserResponse])
async def read_users(db: Session = Depends(get_db),user:UserResponse = Depends(get_current_user)):
    """
    Get a list of all users.
    Requires authentication with an admin role.
    Returns:
    -------
    List[UserResponse]
        A list of all users.
    """
    if user.role == "admin":
        users = db.query(models.User).all()
        return users
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Only Admin can access this route")

@user_router.get('/users/me',response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Get the current user.
    Requires authentication.
    Returns:
    -------
    UserResponse
        The current user.
    """
    return current_user


@user_router.get('/users/{id}',response_model=UserResponse)
async def read_user(id: str,db: Session = Depends(get_db),user:UserResponse = Depends(get_current_user)):
    """
    Get a user by ID.
    Requires authentication with an admin role.
    Parameters:
    ----------
    id : str
        The ID of the user to retrieve.
    db : Session
        The database session dependency.
    user : UserResponse
        The currently authenticated user dependency.
    Returns:
    -------
    UserResponse
        The retrieved user.
    Raises:
    ------
    HTTPException
        If the user is not found, or if the current user is not authorized to retrieve the user.
    """
    if user.role == "admin":
        users = db.query(models.User).filter(models.User.id == id).first()
        return users
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Only Admin can access this route")

@user_router.delete('/users/{id}')
async def delete_user(id: str,db: Session = Depends(get_db),user:UserResponse = Depends(get_current_user)):
    """
    Delete a user by ID.
    Requires authentication with an admin role.
    Parameters:
    ----------
    id : str
        The ID of the user to be deleted.
    db : Session
        The database session dependency.
    user : UserResponse
        The currently authenticated user dependency.
    Returns:
    -------
    dict
        A message indicating the successful deletion of the user.
    Raises:
    ------
    HTTPException
        If the user is not found, or if the current user is not authorized to delete the user.
    """
    if user.role == "admin":
        user_to_delete = db.query(models.User).filter(models.User.id == id).first()
        if user_to_delete is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")
        db.delete(user_to_delete)
        db.commit()
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You are not authorized to delete this user")

@user_router.put('/users/me',response_model=UserResponse)
async def update_user_me(updated_data:UpdateUser,db: Session = Depends(get_db),current_user:UserResponse = Depends(get_current_user)):
    """
    Update the current user's email and password.
    Requires authentication.
    Parameters:
    ----------
    updated_data : UpdateUser
        The updated user data.
    db : Session
        The database session dependency.
    current_user : UserResponse
        The currently authenticated user dependency.
    Returns:
    -------
    UserResponse
        The updated user.
    Raises:
    ------
    HTTPException
        If the user is not found, or if the current user is not authorized to update the user.
    """
    print(updated_data.email)
    user_to_update = db.query(models.User).filter(models.User.id == current_user.id).first()
    print(user_to_update.email)
    if user_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Please Register")
    user_to_update.email = updated_data.email
    user_to_update.hashed_password = get_password_hash(updated_data.password)
    db.commit()
    db.refresh(user_to_update)
    return user_to_update


@user_router.put('/users/{id}',response_model=UserResponse)
async def update_user_role(id: str,user: UserResponse,db: Session = Depends(get_db),current_user:UserResponse = Depends(get_current_user)):
    """
    Update a user's role.
    Requires authentication with an admin role.
    Parameters:
    ----------
    id : str
        The user ID to update.
    user : UserResponse
        The updated user data.
    db : Session
        The database session dependency.
    current_user : UserResponse
        The currently authenticated user dependency.
    Returns:
    -------
    UserResponse
        The updated user.
    Raises:
    ------
    HTTPException
        If the user is not found, or if the current user is not authorized to update the user.
    """
    if current_user.role == "admin":
        user_to_update = db.query(models.User).filter(models.User.id == id).first()
        if user_to_update is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")
        user_to_update.role = user.role
        db.commit()
        db.refresh(user_to_update)
        return user_to_update
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You are not authorized to update this user")

