from fastapi import APIRouter, HTTPException, status
from db.models.users import User
from db.schemas.user import user_schema
from db.client import db_client
from bson import ObjectId

router = APIRouter(
    prefix="/usersdb",
    tags=["users_db"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}
)


@router.get("/")
async def get_users():
    users = db_client.local.users.find()
    return [user_schema(user) for user in users]


@router.get("/{id}")
async def get_user(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Formato de ID inválido")

    user = db_client.local.users.find_one({"_id": ObjectId(id)})
    if user:
        return user_schema(user)

    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.get("/{id}")
async def get_user(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Formato de ID inválido")

    user = db_client.local.users.find_one({"_id": ObjectId(id)})
    if user:
        return user_schema(user)

    raise HTTPException(status_code=404, detail="Usuario no encontrado")


@router.post("/")
async def create_user(user: User):
    user_dict = user.model_dump()
    if "_id" in user_dict:
        del user_dict["_id"]

    inserted_id = db_client.local.users.insert_one(user_dict).inserted_id
    new_user = db_client.local.users.find_one({"_id": inserted_id})
    return {
        "message": "Usuario creado exitosamente",
        "user": user_schema(new_user)
    }


@router.put("/")
async def update_user(user: User):
    user_dict = user.model_dump()

    # Extraemos el _id o el id
    user_id = user_dict.get("_id") or user_dict.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Falta el campo 'id' o '_id'")

    # Validamos y convertimos el ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Formato de ID inválido")

    # Convertimos a ObjectId y eliminamos del cuerpo del update
    obj_id = ObjectId(user_id)
    user_dict.pop("_id", None)
    user_dict.pop("id", None)

    result = db_client.local.users.update_one({"_id": obj_id}, {"$set": user_dict})

    if result.matched_count == 1:
        updated_user = db_client.local.users.find_one({"_id": obj_id})
        return {
            "message": "Usuario actualizado exitosamente",
            "user": user_schema(updated_user)
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado para actualizar"
    )
    
    
@router.delete("/{id}")
async def delete_user(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Formato de ID inválido")

    result = db_client.local.users.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return {"message": "Usuario eliminado exitosamente"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado para eliminar"
    )

