from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate
from passlib.context import CryptContext
# This is part of user authentication system, this is for securely storing passwords in database
# CryptContext gives a simple way to hashpasswords, and algorithm used is bcrypt
# deprecated = "auto" for setting the old hashing methods as deprecated and use the new one
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_email(db: AsyncSession, email:str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        username = user.username,
        email = user.email,
        password = hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def verify_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if user and pwd_context.verify(password, user.password):
        return user
    return None

async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()