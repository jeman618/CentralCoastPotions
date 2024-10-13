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

    """ """ 
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():

    ml_g = "SELECT SUM(num_green_ml) FROM global_inventory"
    ml_r = "SELECT SUM(num_red_ml) FROM global_inventory"
    ml_b = "SELECT SUM(num_blue_ml) FROM global_inventory"


    with db.engine.begin() as connection:
        num_green = connection.execute(sqlalchemy.text(ml_g)).scalar()
        num_red = connection.execute(sqlalchemy.text(ml_r)).scalar()
        num_blue = connection.execute(sqlalchemy.text(ml_b)).scalar()

    all_ml = [num_green, num_red, num_blue, 0]
    potion_type = []
    quantity = 0
    num_p = 0
    ml = ""
    """
    Go from barrel to bottle.
    """
    List = [PotionInventory(potion_type = [0,0,0,0], quantity = 0)]
    plan = []
    for bottle in List:

        if (sum(all_ml) > 0):
            if (max(all_ml) == num_red):
                potions = "UPDATE global_inventory SET num_red_potions = (num_red_potions + :p_amount)"
                ml = "UPDATE global_inventory SET num_red_ml = (num_red_ml - :ml_amount)"
                bottle.potion_type = [100, 0, 0, 0]
                num_p = int(num_red/100)
            elif(max(all_ml) == num_green):
                potions = "UPDATE global_inventory SET num_blue_potions = (num_blue_potions + :p_amount)"
                ml = "UPDATE global_inventory SET num_blue_ml = (num_blue_ml - :ml_amount)"
                bottle.potion_type = [0, 100, 0, 0]
                num_p = int(num_green/100)
            elif (max(all_ml) == num_blue):
                potions = "UPDATE global_inventory SET num_blue_potions = (num_blue_potions + :p_amount)"
                ml = "UPDATE global_inventory SET num_blue_ml = (num_blue_ml - :ml_amount)"
                bottle.potion_type = [0, 0, 100, 0]
                num_p = int(num_blue/100)
            else:
                potions = "UPDATE global_inventory SET num_red_potions = (num_red_potions + :p_amount)"
                ml = "UPDATE global_inventory SET num_red_ml = (num_red_ml - :ml_amount)"
                bottle.potion_type = [100, 0, 0, 0]
                num_p = int(num_red/100)

            plan.append({
                "potion_type": bottle.potion_type,
                "quantity": bottle.quantity,
                })
            
    if (sum(all_ml) > 0):
        with db.engine.begin() as connection:
            ml_update = connection.execute(sqlalchemy.text(ml),{"ml_amount": bottle.quantity * 100})
            potions_update = connection.execute(sqlalchemy.text(potions),{"p_amount": bottle.quantity})


    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    print(plan)
    return plan

if __name__ == "__main__":
    print(get_bottle_plan())
