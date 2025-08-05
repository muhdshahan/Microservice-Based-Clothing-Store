from fastapi import APIRouter, Depends
from app.schemas.product import ProductOut, BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.product import Product
from sqlalchemy.future import select

router = APIRouter(prefix="product", tags=["product"])

@router.post("/",response_model=ProductOut)
async def create(prdt: BaseModel,db: AsyncSession = Depends(get_db)):
    new_product = Product(
        name=prdt.name,
        price=prdt.price
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

@router.put("/{prdt_id}",response_model=ProductOut)
async def update(prdt_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == prdt_id))
    prdt = result.scalar_one_or_none()
    db.add(prdt)
    await db.commit()
    await db.refresh(prdt)
    return prdt