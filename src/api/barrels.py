from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import logging
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

logger = logging.getLogger("barrels")

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(barrels_delivered)

    gold = "UPDATE global_inventory SET gold = gold - :price"
    potions_g = "SELECT num_green_potions FROM global_inventory"
    potions_r = "SELECT num_red_potions FROM global_inventory"
    potions_b = "SELECT num_blue_potions FROM global_inventory"

    for barrels in barrels_delivered:
        print(barrels.potion_type)

        with db.engine.begin() as connection:
            num_green = connection.execute(sqlalchemy.text(potions_g)).scalar()
            num_red = connection.execute(sqlalchemy.text(potions_r)).scalar()
            num_blue = connection.execute(sqlalchemy.text(potions_b)).scalar()
            

        potion = [num_green, num_red, num_blue]

        if (min(potion) == num_red):
                ml = "UPDATE global_inventory SET num_red_ml = (num_red_ml + :mls)"
        elif(min(potion) == num_green):
                ml = "UPDATE global_inventory SET num_green_ml = (num_green_ml + :mls)"
        elif(min(potion) == num_blue):
                ml = "UPDATE global_inventory SET num_blue_ml = (num_blue_ml + :mls)"
        else:
                ml = "UPDATE global_inventory SET num_red_ml = (num_red_ml + :mls)"

        with db.engine.begin() as connection:
            ml_update = connection.execute(sqlalchemy.text(ml),
                                          {"mls": barrels.ml_per_barrel})
            gold_update = connection.execute(sqlalchemy.text(gold),{"price": barrels.price})

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]): 

    gold = "SELECT gold FROM global_inventory"
    potions_g = "SELECT num_green_potions FROM global_inventory"
    potions_r = "SELECT num_red_potions FROM global_inventory"
    potions_b = "SELECT num_blue_potions FROM global_inventory"

    with db.engine.begin() as connection:
                result1 = connection.execute(sqlalchemy.text(gold)).scalar()
                num_green = connection.execute(sqlalchemy.text(potions_g)).scalar()
                num_red = connection.execute(sqlalchemy.text(potions_r)).scalar()
                num_blue = connection.execute(sqlalchemy.text(potions_b)).scalar()

    gold_amount = result1
    all_potions = [num_green, num_red, num_blue]

    for barrel in wholesale_catalog:

        if (sum(all_potions) < 10 and gold_amount > 0 and barrel.price <= gold_amount):
            if (min(all_potions) == num_red):
                barrel.potion_type = [100, 0, 0]
            elif(min(all_potions) == num_green):
                barrel.potion_type = [0, 100, 0]
            elif(min(all_potions) == num_blue):
                barrel.potion_type = [0, 0, 100]
            else:
                barrel.potion_type = [100, 0, 0]
            barrel.quantity += 1
            
    return [{"sku": barrel.sku,
            "ml_per_barrel": barrel.ml_per_barrel,
            "potion_type": barrel.potion_type,
            "quantity": barrel.quantity,
            "price": barrel.price}]
        
    


