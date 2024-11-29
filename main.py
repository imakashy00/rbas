from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from auth.auth import auth_router
from api.blog import blog_router
from api.users import user_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, I am home route created by Akash Yadav"}

app.include_router(auth_router,tags=["Authentication"])
app.include_router(blog_router,tags=["Blogs"])
app.include_router(user_router,tags=["Users"])



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)