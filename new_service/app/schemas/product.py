from pydantic import BaseModel

class BaseProduct(BaseModel):
    name: str
    price: float
    
class ProductOut(BaseProduct):
    id: int
    
    class config():
        orm_mode = True