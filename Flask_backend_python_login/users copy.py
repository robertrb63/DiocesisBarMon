from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    surname: str
    age: int
    email: str
    
    
users = [
    User(id=1, name="John Doe", surname="Doe", age=30, email="john.doe@example.com"),
    User(id=2, name="Jhon Smith", surname="Smith", age=25, email="jhon.smith@example.com"),
    User(id=3, name="Robert Bob", surname="Bob", age=25, email="robert.bob@example.com")
]

@app.get("/users")
async def get_users():
    return users

@app.get("/user/{id}")
async def get_user(id: int):
    return search_user(id)

@app.get("/user2/{id}")
async def get_user2(id: int):
    return search_user2(id)

def search_user(id: int):
    user = next(filter(lambda u: u.id == id, users), None)
    if user:
        return user
    return {"error": "Usuario no encontrado"}


def search_user2(id: int):
    user = filter(lambda u: u.id == id, users)
    try:
        return list(user)
    except:
        return {"error": "Usuario no encontrado"}

"""
@app.post("/user/")
async def create_user(user: User):
    if type(search_user2(user.id)) == User:
        return {"error": "Usuario ya existe"} 
    else:  
        users.append(user)
        return {"message": "Usuario creado exitosamente", "user": user} 
"""
@app.post("/user/")
async def create_user(user: User):
    existing_user = search_user2(user.id)
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    users.append(user)
    return {"message": "Usuario creado exitosamente", "user": user}



"""
@app.put("/user/")
async def update_user(user: User):
    found = False
    for index, existing_user in enumerate(users):
        if existing_user.id == user.id:
            users[index] = user
            return {"message": "Usuario actualizado exitosamente", "user": user}
    if not found:
        return {"error": "Usuario no encontrado para actualizar"}
"""
   
@app.put("/user/")
async def update_user(user: User):
    for index, existing_user in enumerate(users):
        if existing_user.id == user.id:
            users[index] = user
            return {"message": "Usuario actualizado exitosamente", "user": user}
    raise HTTPException(status_code=404, detail="Usuario no encontrado para actualizar")


"""
@app.delete("/user/")
async def delete_user(user: User):
    for index, existing_user in enumerate(users):
        if existing_user.id == user.id:
            del users[index]
            return {"message": "Usuario eliminado exitosamente"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado para eliminar")
"""

@app.delete("/user/{id}")
async def delete_user(id: int):
    for existing_user in users:
        if existing_user.id == id:
            users.remove(existing_user)
            return {"message": "Usuario eliminado exitosamente"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado para eliminar")
