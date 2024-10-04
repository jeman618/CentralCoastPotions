from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    with db.engine.begin() as connection:
        result1 =  "UPDATE global_inventory SET num_green_ml = num_green_ml + 100"
        connection.execute(sqlalchemy.text(result1))

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# hello there
# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]): 
    gold = "SELECT gold FROM global_inventory"
    potions = "SELECT num_green_potions FROM global_inventory"

    
    with db.engine.begin() as connection:
                result1 = connection.execute(sqlalchemy.text(gold)).scalar()
                result2 = connection.execute(sqlalchemy.text(potions)).scalar()

    gold_amount = result1
    potions_amount = result2

    quantity = 0

    for barrel in wholesale_catalog:
        if (potions_amount >= 0):
             quantity += 1

    print(quantity)
    print(wholesale_catalog)

    return [
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": quantity,
        }
    ]


