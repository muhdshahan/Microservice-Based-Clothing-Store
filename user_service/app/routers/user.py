from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserOut
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import user as crud_user
from app.utils.logger import logger
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.jwt_handler import get_current_user, create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await crud_user.verify_user(db, email = form_data.username, password = form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    # Include role in the JWT payload
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "user_id": user.id })
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
async def read_current_user(current_user: UserOut = Depends(get_current_user)):
    return current_user

@router.post("/register", response_model=UserOut)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await crud_user.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = await crud_user.create_user(db, user)
    logger.info(f"User created: {new_user.email}")
    return new_user

@router.get("/",response_model=list[UserOut])
async def read_users(db: AsyncSession = Depends(get_db)):
    return await crud_user.get_users(db)

@router.get("/{user_id}", response_model=UserOut)
async def read_a_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_user.get_a_user(db, user_id)
 