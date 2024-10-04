from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
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
    quantity = 0
    gold_paid = 100
    green_ml =  "UPDATE global_inventory SET num_green_ml = num_green_ml + 100"
    potions = "SELECT num_green_potions FROM global_inventory"
    gold = "UPDATE global_inventory SET gold = gold - 100"

    with db.engine.begin() as connection:
       update_green_ml = connection.execute(sqlalchemy.text(green_ml))
       potions_amount = connection.execute(sqlalchemy.text(potions)).scalar()
       gold_amount = connection.execute(sqlalchemy.text(gold)).scalar()
    
    for barrels in barrels_delivered:
         if potions_amount < 10 and gold_amount > 0:
            barrels_delivered.append("Green", 1000, barrels.potion_type. barrels.quantity)

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
        if (potions_amount >= 0 and gold_amount > 0):
             quantity += 1

    return [
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": quantity,
        }
    ]


