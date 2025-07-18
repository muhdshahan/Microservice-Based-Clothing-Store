from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # loading variables from .env

DATABASE_URL = os.getenv("DATABASE_URL")

# Create asynchronous engine to connect to PostgreSQL database asynchronously
engine = create_async_engine(DATABASE_URL, echo=True)

# Session factory using async session to interact with the database in routes and CRUD operations
AsyncSessionLocal = sessionmaker(
    autocommit=False,        # Ensures transactions are commited by us only giving us full control over when changes are saved
    autoflush=False,         # Prevents automatic flushing of pending changes to DB before queries, so better more control in transactions
    bind=engine,             
    class_=AsyncSession,     # specifies session should use asynchrnous AsyncSession class
    expire_on_commit=False   # prevents ORM objects from being expired (requiring a reload) after committing a transaction
)

# Base class for models to declare models
Base = declarative_base()

# Dependency for FastAPI routes, this yields a DB session to use via FastAPI dependency injection
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session