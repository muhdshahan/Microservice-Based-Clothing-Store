from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate

async def create_item(db: AsyncSession, item: ItemCreate):
    new_item = Item(**item.dict())  # item.dict() converts a Pydantic model instance into Python dictionary
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item

async def get_all_items(db: AsyncSession):
    result = await db.execute(select(Item))
    return result.scalars().all()

async def get_item_by_id(db: AsyncSession, item_id: int):
    return await db.get(Item, item_id)

async def update_item(db: AsyncSession, item_id: int, item_data: ItemUpdate):
    item = await db.get(Item, item_id)
    if not item:
        return None
    # item_data.dict(exclude_unset=True) → returns only the fields that were provided in the request.
    # setattr(item, key, value) → updates each field of the SQLAlchemy model dynamically.
    for key, value in item_data.dict(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item

async def delete_item(db: AsyncSession, item_id: int):
    item = await db.get(Item, item_id)
    if not item:
        return None
    await db.delete(item)
    await db.commit()
    return {"message": "deleted"}