from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate

async def create_order(db: AsyncSession, order: OrderCreate):
    new_order = Order(**order.dict())
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order

async def get_all_orders(db: AsyncSession):
    result = await db.execute(select(Order))
    return result.scalars().all()

async def get_order_by_id(db: AsyncSession, order_id: int):
    return await db.get(Order, order_id)

async def update_order(db: AsyncSession, order_id: int, order_data: OrderUpdate):
    order = await db.get(Order, order_id)
    if not order:
        return None
    for key, value in order_data.dict(exclude_unset=True).items():
        setattr(order, key, value)
    await db.commit()
    await db.refresh(order)
    return order

async def delete_order(db: AsyncSession, order_id: int):
    order = await db.get(Order, order_id)
    if not order:
        return None
    await db.delete(order)
    await db.commit()
    return {"message": "deleted"}
