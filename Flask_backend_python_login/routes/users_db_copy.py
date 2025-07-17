from fastapi import APIRouter, HTTPException, status
from db.models.users import User
from db.schemas.user import user_schema
from db.client import db_client
from bson import ObjectId
from fastapi import FastAPI

app = FastAPI()

# 👇 Middleware de CORS

router = APIRouter(
    prefix="/usersdb",
    tags=["users_db"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}
)

# 🔍 Utilidad: comprobar si ya existe un email
def email_exists(email: str) -> bool:
    return db_client.local.users.find_one({"email": email.lower().strip()}) is not None

# 📋 Obtener todos los usuarios
@router.get("/", response_model=list[User] | None)
async def get_users():
    users = db_client.local.users.find()
    return [user_schema(user) for user in users]

# 🔎 Obtener usuario por ID
@router.get("/{id}")
async def get_user(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Formato de ID inválido")

    user = db_client.local.users.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user_schema(user)


# ➕ Crear nuevo usuario
@router.post("/")
async def create_user(user: User):
    # Normaliza el correo antes de buscar
    normalized_email = user.email.lower().strip()

    if email_exists(normalized_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este correo electrónico"
        )

    user_dict = user.model_dump()
    user_dict.pop("id", None)
    user_dict["email"] = normalized_email  # Guarda el correo normalizado

    inserted_id = db_client.local.users.insert_one(user_dict).inserted_id
    new_user = db_client.local.users.find_one({"_id": inserted_id})

    return {
        "message": "Usuario creado exitosamente",
        "user": user_schema(new_user)
    }

# ✏️ Actualizar usuario existente
@router.put("/")
async def update_user(user: User):
    user_dict = user.model_dump()
    user_id = user_dict.get("id")

    if not user_id or not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID inválido o ausente")

    obj_id = ObjectId(user_id)
    user_dict.pop("id", None)

    # Normaliza el correo antes de actualizar
    if "email" in user_dict:
        user_dict["email"] = user_dict["email"].lower().strip()

    result = db_client.local.users.update_one({"_id": obj_id}, {"$set": user_dict})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado para actualizar")

    updated_user = db_client.local.users.find_one({"_id": obj_id})
    return {
        "message": "Usuario actualizado exitosamente",
        "user": user_schema(updated_user)
    }

# 🗑️ Eliminar usuario
@router.delete("/{id}")
async def delete_user(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Formato de ID inválido")

    result = db_client.local.users.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado para eliminar")

    return {"message": "Usuario eliminado exitosamente"}