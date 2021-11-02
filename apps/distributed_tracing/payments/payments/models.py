from pydantic import BaseModel
class Order(BaseModel):
    item_id: int
    quantity: int
    price: float

