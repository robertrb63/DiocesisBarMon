from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: str | None
    nombre: str
    telefono: str
    email: EmailStr
    poblacion: str
    grupo_parroquial: str
    unidad: str
    moderador: str
    tel_moderador: str
    arciprestazgo: str
    arcipreste: str
    tel_arciprestazgo: str
    animador: str
    tel_animador: str