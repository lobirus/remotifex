"""Authentication routes: login, setup."""

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongodb import get_db
from app.models.user import create_user_doc
from app.schemas.user import LoginRequest, LoginResponse, SetupRequest, UserResponse
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Authenticate user and return JWT token."""
    user = await db.users.find_one({"username": request.username})
    if user is None or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    user_id = str(user["_id"])
    token = create_access_token(user_id)

    return LoginResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            username=user["username"],
            is_admin=user["is_admin"],
        ),
    )


@router.post("/setup", response_model=LoginResponse)
async def setup(
    request: SetupRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Create the initial admin user. Only works if no users exist."""
    existing_count = await db.users.count_documents({})
    if existing_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setup already completed. Use login instead.",
        )

    doc = create_user_doc(
        username=request.username,
        password_hash=hash_password(request.password),
        is_admin=True,
    )
    result = await db.users.insert_one(doc)
    user_id = str(result.inserted_id)
    token = create_access_token(user_id)

    return LoginResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            username=request.username,
            is_admin=True,
        ),
    )
