from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.item import ItemCreate, ItemUpdate, ItemOut
from app.crud.item import (
    create_item, get_all_items, get_item_by_id,
    update_item, delete_item
)
from app.db.database import get_db
from app.utils.logger import logger
from app.utils.metrics import REQUEST_COUNT

router = APIRouter(prefix="/items", tags=["Inventory"])

@router.post("/", response_model=ItemOut)
async def create_new_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    REQUEST_COUNT.labels(endpoint="/items/", method="POST").inc()
    logger.info("Creating new item", extra={"item": item.name})
    return await create_item(db, item)

@router.get("/", response_model=List[ItemOut])
async def read_all_items(db: AsyncSession = Depends(get_db)):
    REQUEST_COUNT.labels(endpoint="/items/", method="GET").inc()
    return await get_all_items(db)

@router.get("/{item_id}", response_model=ItemOut)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    REQUEST_COUNT.labels(endpoint="/items/{item_id}", method="GET").inc()
    item = await get_item_by_id(db, item_id)
    if not item:
        logger.warning("Item not found", extra={"item_id": item_id})
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=ItemOut)
async def update_existing_item(item_id: int, item_data: ItemUpdate, db: AsyncSession = Depends(get_db)):
    REQUEST_COUNT.labels(endpoint="/items/{item_id}", method="PUT").inc()
    updated_item = await update_item(db, item_id, item_data)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info("Item updated", extra={"item_id": item_id})
    return updated_item

@router.delete("/{item_id}")
async def delete_existing_item(item_id: int, db: AsyncSession = Depends(get_db)):
    REQUEST_COUNT.labels(endpoint="/items/{item_id}", method="DELETE").inc()
    result = await delete_item(db, item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info("Item deleted", extra={"item_id": item_id})
    return result
