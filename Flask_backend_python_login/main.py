from fastapi import FastAPI
from routes import products, users, jwt_auth_users, users_db, users_db_copy
from fastapi.staticfiles import StaticFiles

app = FastAPI()


#Routes
app.include_router(products.router, prefix="/api", tags=["products"], responses={404: {"description": "Not found"}})
app.include_router(users.router, prefix="/api", tags=["users"], responses={404: {"description": "Not found"}})
app.include_router(jwt_auth_users.router, prefix="/api", tags=["auth"], responses={404: {"description": "Not found"}})
app.include_router(users_db.router, prefix="/api", tags=["users_db"], responses={404: {"description": "Not found"}})
app.include_router(users_db_copy.router, prefix="/api", tags=["users_db_copy"], responses={404: {"description": "Not found"}})
app.mount("/static", StaticFiles(directory="static"), name="static")
from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # o usa ["*"] para desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/url")
async def root():
    return {"email": "restrepo.roberto@gmail.com"}