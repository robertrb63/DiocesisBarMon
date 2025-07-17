from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import os
from typing import Optional, List
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "a-very-secure-secret-key")  # Debe configurarse en .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Inicialización
app = FastAPI(
    title="API de Autenticación Mejorada",
    description="API con autenticación JWT, roles y refresh tokens",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Ajustar según el frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Modelos Pydantic
class UserBase(BaseModel):
    username: str
    name: str
    email: EmailStr
    disabled: bool = False
    role: str = "user"  # Por defecto, rol de usuario

class UserCreate(UserBase):
    password: str

class User(UserBase):
    class Config:
        from_attributes = True

class UserInDB(UserBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# Base de datos simulada (en memoria)
users_db = {
    "admin": {
        "username": "admin",
        "name": "Admin User",
        "email": "admin@example.com",
        "disabled": False,
        "role": "admin",
        "hashed_password": pwd_context.hash("admin123")
    },
    "user1": {
        "username": "user1",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "disabled": False,
        "role": "user",
        "hashed_password": pwd_context.hash("user123")
    }
}

# Excepciones personalizadas
class AuthException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(status_code=status_code, detail=detail)

# Utilidades
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña."""
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[UserInDB]:
    """Busca un usuario en la base de datos."""
    if username in users_db:
        return UserInDB(**users_db[username])
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token de acceso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Crea un refresh token JWT."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Obtiene el usuario actual a partir del token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise AuthException(detail="Invalid token")
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise AuthException(detail="Invalid token")
    
    user = get_user(token_data.username)
    if user is None:
        raise AuthException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)
    if user.disabled:
        raise AuthException(detail="User is disabled", status_code=status.HTTP_403_FORBIDDEN)
    return user

async def get_current_admin(user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Verifica si el usuario actual es administrador."""
    if user.role != "admin":
        raise AuthException(detail="Insufficient permissions", status_code=status.HTTP_403_FORBIDDEN)
    return user

# Rutas
@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Autentica un usuario y devuelve un access token y un refresh token."""
    user = get_user(form_data.username)
    if not user:
        raise AuthException(detail="Incorrect username or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise AuthException(detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Renueva un access token usando un refresh token."""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise AuthException(detail="Invalid refresh token")
    except JWTError:
        raise AuthException(detail="Invalid refresh token")
    
    user = get_user(username)
    if not user:
        raise AuthException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    new_refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@app.post("/users", response_model=User)
async def create_user(user: UserCreate, current_user: UserInDB = Depends(get_current_admin)):
    """Crea un nuevo usuario (solo para administradores)."""
    if user.username in users_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]
    
    users_db[user.username] = user_dict
    return User(**user_dict)

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """Devuelve los datos del usuario autenticado."""
    return current_user

@app.get("/users", response_model=List[str])
async def list_users(current_user: UserInDB = Depends(get_current_admin)):
    """Lista todos los nombres de usuario (solo para administradores)."""
    return list(users_db.keys())