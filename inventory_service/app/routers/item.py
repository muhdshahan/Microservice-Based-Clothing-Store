from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.item import ItemCreate, ItemUpdate, ItemOut, QuantityUpdate
from app.crud.item import (
    create_item, get_all_items, get_item_by_id,
    update_item, delete_item
)
from app.db.database import get_db
from app.utils.logger import logger
from app.utils.metrics import REQUEST_COUNT
from app.auth.jwt_handler import get_current_user  # Decodes JWT, includes role

router = APIRouter(prefix="/items", tags=["Inventory"])

# Only Admins can create new items
@router.post("/", response_model=ItemOut)
async def create_new_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_db),
    user_info: dict = Depends(get_current_user)
):
    REQUEST_COUNT.labels(
    method="post",        # Must match your metric definition (lowercase)
    path="items",         # "path" instead of "endpoint"
    status_code="201"     # Add status code (201 for created)
).inc()
    
    if user_info["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create new items"
        )
    
    logger.info(
        f"Admin '{user_info['email']}' is creating new item '{item.name}'",
        extra={"item": item.name, "user": user_info['email']}
    )
    return await create_item(db, item)

# Open to all authenticated users
@router.get("/", response_model=List[ItemOut])
async def read_all_items(db: AsyncSession = Depends(get_db)):
    REQUEST_COUNT.labels(method="get", path="items", status_code="200").inc()
    return await get_all_items(db)

@router.get("/{item_id}", response_model=ItemOut)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    try:
        item = await get_item_by_id(db, item_id)
        if not item:
            logger.warning("Item not found", extra={"item_id": item_id})
            REQUEST_COUNT.labels(method="get", path="items/{id}", status_code="404").inc()
            raise HTTPException(status_code=404, detail="Item not found")
        
        REQUEST_COUNT.labels(method="get", path="items/{id}", status_code="200").inc()
        return item
    except Exception as e:
        REQUEST_COUNT.labels(method="get", path="items/{id}", status_code="500").inc()
        raise e

# Only Admins can update items
@router.put("/{item_id}", response_model=ItemOut)
async def update_existing_item(
    item_id: int,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    user_info: dict = Depends(get_current_user)
):
    try:
        if user_info["role"] != "admin":
            REQUEST_COUNT.labels(method="put", path="items/{id}", status_code="403").inc()
            raise HTTPException(status_code=403, detail="Only admins can update items")

        updated_item = await update_item(db, item_id, item_data)
        if not updated_item:
            REQUEST_COUNT.labels(method="put", path="items/{id}", status_code="404").inc()
            raise HTTPException(status_code=404, detail="Item not found")
        
        logger.info("Item updated", extra={"item_id": item_id, "user": user_info['email']})
        REQUEST_COUNT.labels(method="put", path="items/{id}", status_code="200").inc()
        return updated_item
    except Exception as e:
        REQUEST_COUNT.labels(method="put", path="items/{id}", status_code="500").inc()
        raise e

# Only Admins can delete items
@router.delete("/{item_id}")
async def delete_existing_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    user_info: dict = Depends(get_current_user)
):
    try:
        if user_info["role"] != "admin":
            REQUEST_COUNT.labels(method="delete", path="items/{id}", status_code="403").inc()
            raise HTTPException(status_code=403, detail="Only admins can delete items")

        result = await delete_item(db, item_id)
        if not result:
            REQUEST_COUNT.labels(method="delete", path="items/{id}", status_code="404").inc()
            raise HTTPException(status_code=404, detail="Item not found")
        
        logger.info("Item deleted", extra={"item_id": item_id, "user": user_info['email']})
        REQUEST_COUNT.labels(method="delete", path="items/{id}", status_code="200").inc()
        return result
    except Exception as e:
        REQUEST_COUNT.labels(method="delete", path="items/{id}", status_code="500").inc()
        raise e


@router.put("/{item_id}/decrease")
async def decrease_quantity(item_id: int, data: QuantityUpdate, db: AsyncSession = Depends(get_db)):
    item = await get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.quantity < data.qty:
        raise HTTPException(status_code=400, detail="Out of Stock")
    item.quantity -= data.qty
    await db.commit()
    return {"message": "Quantity decreased", "remaining": item.quantity}
    
@router.put("/{item_id}/increase")
async def increase_quantity(item_id: int, data: QuantityUpdate, db: AsyncSession = Depends(get_db)):
    item = await get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.quantity += data.qty
    await db.commit()
    return {"message": "Quantity increased", "current": item.quantity}