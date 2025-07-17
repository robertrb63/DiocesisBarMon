def user_schema(user) -> dict:
    return {
        "id": str(user.get("_id", "")),
        "nombre": user.get("nombre", ""),
        "telefono": user.get("telefono", ""),
        "email": user.get("email", ""),
        "poblacion": user.get("poblacion", ""),
        "grupo_parroquial": user.get("grupo_parroquial", ""),
        "unidad": user.get("unidad", ""),
        "moderador": user.get("moderador", ""),
        "tel_moderador": user.get("tel_moderador", ""),
        "arciprestazgo": user.get("arciprestazgo", ""),
        "arcipreste": user.get("arcipreste", ""),
        "tel_arciprestazgo": user.get("tel_arciprestazgo", ""),
        "animador": user.get("animador", ""),
        "tel_animador": user.get("tel_animador", "")
    }
    
    
    def users_schema(users: list) -> list:
        return [user_schema(user) for user in users]
