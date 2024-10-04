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

    with db.engine.begin() as connection:
        sql_to_execute = """UPDATE global_inventory 
                            SET num_green_potions = num_green_potions + 1"""
        connection.execute(sqlalchemy.text(sql_to_execute)) 

    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():

    quantity = 0
    num_potions = "UPDATE global_inventory SET num_green_potions = num_green_potions - 1"
    green_ml = "SELECT num_green_ml FROM global_inventory"

    with db.engine.begin() as connection:
        update_num_potions = connection.execute(sqlalchemy.text(num_potions))
        green_ml_amount = connection.execute(sqlalchemy.text(green_ml)).scalar()
    """
    Go from barrel to bottle.
    """
    for bottle in range(5):
        if green_ml_amount > 0:
            quantity += 1

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": quantity,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())
