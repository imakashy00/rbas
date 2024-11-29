import re
from typing import List
from fastapi import APIRouter,Depends,HTTPException,status
from database import models
from sqlalchemy.orm import Session
from database.db import get_db
from database.schema import BlogResponse, UserResponse,BlogCreate
from auth.auth import get_current_user


blog_router = APIRouter()


@blog_router.get("/allblogs",response_model=List[BlogResponse])
async def read_blogs(db: Session = Depends(get_db),user:UserResponse = Depends(get_current_user)):
    """
    Retrieve all blogs from the database.

    This endpoint allows access only to users with 'admin' or 'moderator' roles.
    If the user is authorized, it returns a list of all blogs. If not, it raises an
    HTTP 401 Unauthorized exception.
    Parameters:
    ----------
    db : Session
        The database session dependency.
    user : UserResponse
        The currently authenticated user dependency.
    Returns:
    -------
    List[BlogResponse]
        A list of all blogs.

    Raises:
    ------
    HTTPException
        If the current user is not authorized to access this route.
    """
    if user.role == "admin" or user.role == "moderator":
        blogs = db.query(models.Blog).all()
        if blogs is not None:
            return blogs
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Only Admin and moderator can access this route")

@blog_router.get("/yourblogs",response_model=List[BlogResponse])
async def read_your_blogs(db: Session = Depends(get_db),user:UserResponse = Depends(get_current_user)):
    """
    Retrieve all blogs created by the currently authenticated user.
    This endpoint is accessible to any authenticated user. It returns a list of all
    blogs created by the user.
    Parameters:
    ----------
    db : Session
        The database session dependency.
    user : UserResponse
        The currently authenticated user dependency.

    Returns:
    -------
    List[BlogResponse]
        A list of all blogs created by the user.
    """
    
    blogs = db.query(models.Blog).filter(models.Blog.user_id == user.id).all()
    return blogs


@blog_router.get("/blog/{id}",response_model=BlogResponse )
async def read_blog(id: str,db: Session = Depends(get_db),user:UserResponse = Depends(get_current_user)):
    """
    Retrieve a blog by ID.

    This endpoint is accessible to any authenticated user. It returns a single blog
    with the specified ID.

    Parameters:
    ----------
    id : str
        The ID of the blog to retrieve.
    db : Session
        The database session dependency.
    user : UserResponse
        The currently authenticated user dependency.

    Returns:
    -------
    BlogResponse
        A single blog with the specified ID.

    Raises:
    ------
    HTTPException
        If the blog is not found.
    """
    blog = db.query(models.Blog).filter(models.Blog.id == id ).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="blog not found")
    return blog
    
@blog_router.post("/blog",response_model= BlogResponse,status_code=status.HTTP_201_CREATED)     
async def create_blog(blog: BlogCreate,db: Session = Depends(get_db),user:UserResponse = Depends(get_current_user)):
    """
    Create a new blog.
    This endpoint is accessible to any authenticated user. It returns the newly created blog.
    Parameters:
    ----------
    blog : BlogCreate
        The blog to create.
    db : Session
        The database session dependency.
    user : UserResponse
        The currently authenticated user dependency.

    Returns:
    -------
    BlogResponse
        The newly created blog.
    """
    new_blog = models.Blog(title=blog.title,body=blog.body,user_id=user.id)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@blog_router.put("/blog/{id}",response_model=BlogResponse)
async def update_blog(id: str,blog: BlogCreate,db: Session = Depends(get_db),user:UserResponse = Depends(get_current_user)):
    """
    Update a blog by ID.
    This endpoint is accessible to the blog owner, moderator and admin.
    It returns the updated blog.
    Parameters:
    ----------
    id : str
        The ID of the blog to update.
    blog : BlogCreate
        The updated blog.
    db : Session
        The database session dependency.
    user : UserResponse
        The currently authenticated user dependency.
    Returns:
    -------
    BlogResponse
        The updated blog.
    Raises:
    ------
    HTTPException
        If the blog is not found, or if the current user is not authorized to update the blog.
    """
    blog_to_update = db.query(models.Blog).filter(models.Blog.id == id).first()
    if blog_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="blog not found")
    if user.role == "admin" or blog_to_update.user_id == user.id or user.role == "moderator":
        blog_to_update.title = blog.title
        blog_to_update.body = blog.body
        db.commit()
        db.refresh(blog_to_update)
        return blog_to_update
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You are not authorized to update this blog")


@blog_router.delete("/blog/{id}")
async def delete_blog(id: str,db: Session = Depends(get_db),user:UserResponse = Depends(get_current_user)):
    """
    Delete a blog by ID.

    This endpoint is accessible to the blog owner, moderator, and admin.
    It deletes the specified blog if the user has the appropriate permissions.

    Parameters:
    ----------
    id : str
        The ID of the blog to delete.
    db : Session
        The database session dependency.
    user : UserResponse
        The currently authenticated user dependency.

    Returns:
    -------
    dict
        A message indicating the successful deletion of the blog.

    Raises:
    ------
    HTTPException
        If the blog is not found, or if the current user is not authorized to delete the blog.
    """
    blog_to_delete = db.query(models.Blog).filter(models.Blog.id == id).first()
    if blog_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="blog not found")
    if user.role == "admin" or blog_to_delete.user_id == user.id or user.role == "moderator":
        db.delete(blog_to_delete)
        db.commit()
        return {"message": "Blog deleted successfully"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You are not authorized to delete this blog")