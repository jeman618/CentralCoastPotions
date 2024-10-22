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

    deliver_sql = """UPDATE catalog SET 
                        inventory = inventory + :quantity
                        WHERE potion_type = :potion_type"""
    ml_sql = """UPDATE global_inventory SET red_ml = red_ml - :red,
                                            green_ml = green_ml - :green,
                                            blue_ml = blue_ml - :blue,
                                            dark_ml = dark_ml - :dark"""
    red = 0
    green = 0
    blue = 0
    dark = 0
    with db.engine.begin() as connection:

        for new_potions in potions_delivered:

            print(new_potions)
            red += new_potions.potion_type[0] * new_potions.quantity 
            green += new_potions.potion_type[1] * new_potions.quantity
            blue += new_potions.potion_type[2] * new_potions.quantity 
            dark += new_potions.potion_type[3] * new_potions.quantity 

            connection.execute(sqlalchemy.text(deliver_sql), {"quantity": new_potions.quantity,
                                                              "potion_type": new_potions.potion_type})
            
        connection.execute(sqlalchemy.text(ml_sql), {"red": red, "green": green, "blue": blue, "dark": dark})
    """ """ 
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")
    return "OK"

@router.post("/plan")
def get_bottle_plan():

    all_potions_sql = "SELECT sku, inventory, potion_type FROM catalog ORDER BY catalog_id DESC"
    ml_sql = "SELECT red_ml, green_ml, blue_ml, dark_ml FROM global_inventory"
    with db.engine.begin() as connection:
        all_potions = connection.execute(sqlalchemy.text(all_potions_sql)).all()
        ml_total = connection.execute(sqlalchemy.text(ml_sql)).fetchone()

    ml_total = list(ml_total)
    print(ml_total)
    plan = []
    if (sum(ml_total) > 0):

        for possible_potion in all_potions:

            potion_type = possible_potion[2]
            # print(potion_type)

            if (potion_type[0] <= ml_total[0] and potion_type[1] <= ml_total[1] 
                and potion_type[2] <= ml_total[2] and potion_type[3] <= ml_total[3]):
                
                quantity = int ((ml_total[0] * potion_type[0])/10000 + (ml_total[1] * potion_type[1])/10000
                                + (ml_total[2] * potion_type[2])/10000 + (ml_total[3] * potion_type[3])/10000)
                
                ml_total[0] -= potion_type[0]
                ml_total[1] -= potion_type[1]
                ml_total[2] -= potion_type[2]
                ml_total[3] -= potion_type[3]
                
                plan.append({"potion_type": potion_type, "quantity": quantity})

    print(plan)
    return plan

if __name__ == "__main__":
    print(get_bottle_plan())
