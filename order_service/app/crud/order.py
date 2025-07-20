from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate
from app.utils.service_clients import reduce_inventory, increase_inventory

async def create_order(db: AsyncSession, order: OrderCreate):
    new_order = Order(**order.dict())
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order

async def get_all_orders(db: AsyncSession, user_id: int, role: str):
    if role == "admin":
        result = await db.execute(select(Order))
    else:
        result = await db.execute(select(Order).where(Order.user_id == user_id))
    return result.scalars().all()

async def get_order_by_id(db: AsyncSession, order_id: int, user_id: int, role: str):
    if role == "admin":
        result = await db.get(Order, order_id)
    else:
        result = await db.execute(select(Order).where(Order.id == order_id, Order.user_id == user_id))
    return result

async def update_order(db: AsyncSession, order_id: int, order_data: OrderUpdate, user_id: int):
    order = await db.execute(select(Order).where(Order.user_id == user_id))
    if not order:
        return None
    
    old_quantity = order.quantity
    new_quantity = order_data.quantity if order_data.quantity is not None else old_quantity
    
    # Inventory updation (updating products stock quantity)
    if new_quantity > old_quantity:
        diff = new_quantity - old_quantity
        await reduce_inventory(order.item_id, diff)  # Decrease inventory
    elif new_quantity < old_quantity:
        diff = old_quantity - new_quantity
        await increase_inventory(order.item_id, diff)  # Increase inventory
    
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
 