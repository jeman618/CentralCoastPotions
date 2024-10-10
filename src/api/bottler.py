from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):

    ml_g = "SELECT num_green_ml FROM global_inventory"
    ml_r = "SELECT num_red_ml FROM global_inventory"
    ml_b = "SELECT num_blue_ml FROM global_inventory"

    with db.engine.begin() as connection:
            green_ml = connection.execute(sqlalchemy.text(ml_g)).scalar()
            red_ml = connection.execute(sqlalchemy.text(ml_r)).scalar()
            blue_ml = connection.execute(sqlalchemy.text(ml_b)).scalar()

    ml_total = [green_ml, red_ml, blue_ml]

    print(potions_delivered)
    for potion in potions_delivered:
        if (sum(ml_total) > 0):
            if (max(ml_total) == red_ml):
                potions = "UPDATE global_inventory SET num_red_potions = (num_red_potions + :p_amount)"
                ml = "UPDATE global_inventory SET num_red_ml = (num_red_ml - :ml_amount)"
                ml_amount =int(potion.quantity * 100)
            elif(max(ml_total) == green_ml):
                potions = "UPDATE global_inventory SET num_green_potions = (num_green_potions + :p_amount)"
                ml = "UPDATE global_inventory SET num_green_ml = (num_green_ml - :ml_amount)"
                ml_amount =int(potion.quantity * 100)
            elif (max(ml_total) == blue_ml):
                potions = "UPDATE global_inventory SET num_blue_potions = (num_blue_potions + :p_amount)"
                ml = "UPDATE global_inventory SET num_blue_ml = (num_blue_ml - :ml_amount)"
                ml_amount =int(potion.quantity * 100)
            else:
                potions = "UPDATE global_inventory SET num_red_potions = (num_red_potions + :p_amount)"
                ml = "UPDATE global_inventory SET num_red_ml = (num_red_ml - :ml_amount)"
                ml_amount =int(potion.quantity * 100)
    
    with db.engine.begin() as connection:
            ml_update = connection.execute(sqlalchemy.text(ml),{"ml_amount": ml_amount})
            potions_update = connection.execute(sqlalchemy.text(potions),{"p_amount": potion.quantity})

    """ """ 
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():

    ml_g = "SELECT num_green_ml FROM global_inventory"
    ml_r = "SELECT num_red_ml FROM global_inventory"
    ml_b = "SELECT num_blue_ml FROM global_inventory"


    with db.engine.begin() as connection:
        num_green = connection.execute(sqlalchemy.text(ml_g)).scalar()
        num_red = connection.execute(sqlalchemy.text(ml_r)).scalar()
        num_blue = connection.execute(sqlalchemy.text(ml_b)).scalar()

    all_ml = [num_green, num_red, num_blue]
    potion_type = []
    num_p = 0

    if (sum(all_ml) > 0):
            if (max(all_ml) == num_red):
                potion_type = [200, 0, 0]
                num_p = int(num_green/100)
            elif(max(all_ml) == num_green):
                potion_type = [0, 100, 0]
                num_p = int(num_red/100)
            elif (max(all_ml) == num_blue):
                potion_type = [0, 0, 100]
                num_p = int(num_blue/100)
    """
    Go from barrel to bottle.
    """
    quantity = 0
    for bottle in range(num_p):
            quantity += 1
    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    return [
            {
                "potion_type": potion_type,
                "quantity": quantity,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())
