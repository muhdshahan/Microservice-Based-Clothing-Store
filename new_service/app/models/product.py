from app.db.database import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, Float

class Product(Base):
    __tablename__ = "product"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] =  mapped_column(String, nullable=False)
    price: Mapped[float] =  mapped_column(Float, nullable=False)