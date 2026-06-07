from fastapi import APIRouter
from models.user import LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


fake_users = {
    "admin": {
        "password": "admin123",
        "role": "admin"
    },
    "customer": {
        "password": "customer123",
        "role": "customer"
    }
}


@router.post("/login")
def login(user: LoginRequest):
    saved_user = fake_users.get(user.username)

    if not saved_user:
        return {
            "success": False,
            "message": "Invalid username"
        }

    if saved_user["password"] != user.password:
        return {
            "success": False,
            "message": "Invalid password"
        }

    return {
        "success": True,
        "username": user.username,
        "role": saved_user["role"]
    }