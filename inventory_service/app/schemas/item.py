from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    category: str
    quantity: int
    price: float
    
class ItemCreate(ItemBase):
    pass
    
class ItemUpdate(BaseModel):
    # updation for the fields is optional doesnt need to add all field update
    name: str | None = None
    category: str | None = None
    quantity: int | None = None
    price: float | None = None
    
    
class ItemOut(ItemBase):
    id: int
    
    class Config:
        orm_mode = True