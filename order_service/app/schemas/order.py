from pydantic import BaseModel

class OrderBase(BaseModel):
    user_id: int
    item_id: int
    quantity: int
    total_price: float
    status: str = "pending"

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    quantity: int | None = None
    status: str | None = None

class OrderOut(OrderBase):
    id: int

    class Config:
        orm_mode = True
