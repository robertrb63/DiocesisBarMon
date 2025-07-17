
from fastapi import FastAPI, HTTPException, Depends
from fastapi import status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

oauth = OAuth2PasswordBearer(tokenUrl="login")

class User(BaseModel):

    username: str
    name: str
    email: str
    dissable: bool

class UserDB(User):
    password: str

users = {
    "Doe": {"username": "Doe", "name": "John Doe", "email": "john.doe@example.com", "dissable": False, "password": "123"},
    "Smith": {"username": "Smith", "name": "John Smith", "email": "john.smith@example.com", "dissable": True, "password": "321"},
    "Bob": {"username": "Bob", "name": "Robert Bob", "email": "robert.bob@example.com", "dissable": False, "password": "456"}
}

@app.get("/users")
async def get_users():
    return users


def search_user_db(username: str):
    if username in users:
        return UserDB(**users[username])
    raise HTTPException(status_code=404, detail="User not found")


def search_user(username: str):
    if username in users:   
        return User(**users[username])
    raise HTTPException(status_code=404, detail="User not found")


async def current_user(token: str = Depends(oauth)):
    user = search_user(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})
    if user.dissable:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")
    return user

@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users.get(form.username)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username")

    user = search_user_db(form.username)
    if not form.password == user.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/users/me")
async def get_me(user: User = Depends(current_user)):
    return user