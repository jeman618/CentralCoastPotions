from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    num_ml_sql = "SELECT red_ml, green_ml, blue_ml, dark_ml FROM global_inventory"
    num_p_sql = "SELECT SUM(inventory) FROM catalog"
    gold_sql = "SELECT gold FROM global_inventory"
                        
    with db.engine.begin() as connection:
        num_ml = connection.execute(sqlalchemy.text(num_ml_sql)).fetchone()
        total_p = connection.execute(sqlalchemy.text(num_p_sql)).scalar()
        gold = connection.execute(sqlalchemy.text(gold_sql)).scalar()

    total_ml = sum(list(num_ml))

    print(f"number_of_potions: {total_p} ml_in_barrels: {total_ml} gold: {gold}")
    
    return {"number_of_potions": total_p, "ml_in_barrels": total_ml, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():

    num_ml_sql = "SELECT red_ml, green_ml, blue_ml, dark_ml FROM global_inventory"
    num_p_sql = "SELECT SUM(inventory) FROM catalog"
    gold_sql = "SELECT gold FROM global_inventory"
                        
    with db.engine.begin() as connection:
        num_ml = connection.execute(sqlalchemy.text(num_ml_sql)).fetchone()
        num_p= connection.execute(sqlalchemy.text(num_p_sql)).scalar()
        gold = connection.execute(sqlalchemy.text(gold_sql)).scalar()

        potion_cap = 0
        ml_cap = 0

    if gold >= 1000:
        if num_p < 10:
            potion_cap = 1
        if  sum(list(num_ml)) < 100:
            ml_cap = 1
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    return {
        "potion_capacity": potion_cap,
        "ml_capacity": ml_cap
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):

    gl_update = """UPDATE global_inventory SET
                                    red_ml = red_ml + :ml,
                                    green_ml = green_ml + :ml,
                                    blue_ml = blue_ml + :ml,
                                    dark_ml = dark_ml + :ml"""  
    potions_update_sql = "UPDATE catalog SET inventory = inventory + :potion"
    gold_update = "UPDATE global_inventory SET gold = gold - (1000 * :ml_cap) - (1000 * :p_cap)"

    with db.engine.begin() as connection:
            new_inventory = connection.execute(sqlalchemy.text(gl_update), {"ml": int((capacity_purchase.ml_capacity / 4) * 10000)} )
            potions_update = connection.execute(sqlalchemy.text(potions_update_sql), {"potion": int((capacity_purchase.potion_capacity / 4)) + 3} )
            new_gold = connection.execute(sqlalchemy.text(gold_update), {"ml_cap": capacity_purchase.ml_capacity, "p_cap": capacity_purchase.potion_capacity})
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    return "OK"
