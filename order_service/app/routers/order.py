from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.order import OrderCreate, OrderOut, OrderUpdate
from app.crud.order import create_order, get_all_orders, get_order_by_id, update_order, delete_order
from app.utils.logger import logger
from app.auth.jwt_handler import get_current_user
from app.utils.service_clients import get_item_by_id, get_user_by_id

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderOut)
async def create(order: OrderCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    logger.info("Creating order")
    # 1. Validate user
    await get_user_by_id(order.user_id)
    
    # 2. Validate item
    await get_item_by_id(order.item_id)
    
    # 3. Create order
    return await create_order(db, order)

@router.get("/", response_model=list[OrderOut])
async def get_all(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    logger.info("Fetching all orders")
    return await get_all_orders(db)

@router.get("/{order_id}", response_model=OrderOut)
async def get(order_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    logger.info(f"Fetching order {order_id}")
    order = await get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}", response_model=OrderOut)
async def update(order_id: int, order: OrderUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    logger.info(f"Updating order {order_id}")
    
    # Only validate if user_id or item_id is being updated
    if order.user_id is not None:
        await get_user_by_id(order.user_id)
    if order.item_id is not None:
        await get_item_by_id(order.item_id)
    
    updated = await update_order(db, order_id, order)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated

@router.delete("/{order_id}")
async def delete(order_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    logger.info(f"Deleting order {order_id}")
    deleted = await delete_order(db, order_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found")
    return deleted
