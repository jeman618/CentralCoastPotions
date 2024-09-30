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
    with db.engine.begin() as connection:
        sql_update = "SELECT num_green_ml - 1 AS sum_num_green_ml WHERE SUM(num_green_ml) > 0 FROM global_inventory"
        connection.execute(sqlalchemy.text(sql_update))  
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    with db.engine.begin() as connection:
        sql_to_execute = """SELECT num_green_ml FROM global_inventory"""
        result = connection.execute(sqlalchemy.text(sql_to_execute))
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    return [
            {
                "potion_type": [0, 1, 0, 0],
                "quantity": result,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())
