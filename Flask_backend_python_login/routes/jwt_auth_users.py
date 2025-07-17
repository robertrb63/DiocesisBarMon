from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta

# Configuración
ALGORITHM = "HS256"
SECRET_KEY = "your_secret_key"
TIME_TOKEN_EXPIRE = 1  # minutos

crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()
oauth = OAuth2PasswordBearer(tokenUrl="login")

# Modelos
class User(BaseModel):
    username: str
    name: str
    email: str
    dissable: bool

class UserDB(User):
    password: str

# Base de datos simulada
users = {
    "Doe": {
        "username": "Doe",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "dissable": False,
        "password": crypt.hash("1234")
    },
    "Bob": {
        "username": "Bob",
        "name": "Robert Bob",
        "email": "robert.bob@example.com",
        "dissable": False,
        "password": crypt.hash("321")
    },
    "Smith": {"username": "Smith", "name": "John Smith", "email": "john.smith@example.com", "dissable": True, "password": crypt.hash("321")},
}

# Utilidades
def search_user_db(username: str):
    user = users.get(username)
    if user:
        return UserDB(**user)
    return None

def search_user(username: str):
    user = users.get(username)
    if user:
        return User(**user)
    return None

# Rutas
@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = search_user_db(form.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username")
    if not crypt.verify(form.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    
    expire = datetime.utcnow() + timedelta(minutes=TIME_TOKEN_EXPIRE)
    token_data = {"sub": user.username, "exp": expire}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}

async def current_user(token: str = Depends(oauth)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = search_user(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.dissable:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")
    return user

@router.get("/users/me")
async def get_me(user: User = Depends(current_user)):
    return user

@router.get("/users")
async def list_users():
    return list(users.keys())