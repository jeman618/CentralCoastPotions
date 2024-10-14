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
    num_potions_g = "SELECT num_green_potions FROM global_inventory"
    num_potions_b = "SELECT num_red_potions FROM global_inventory"
    num_potions_r = "SELECT num_blue_potions FROM global_inventory"
    num_ml_g = "SELECT num_green_ml FROM global_inventory"
    num_ml_r = "SELECT num_blue_ml FROM global_inventory"
    num_ml_b = "SELECT num_red_ml FROM global_inventory"
    gold_sql = "SELECT gold FROM global_inventory"
                        
    with db.engine.begin() as connection:
        num_p_g = connection.execute(sqlalchemy.text(num_potions_g)).scalar()
        num_p_r = connection.execute(sqlalchemy.text(num_potions_r)).scalar()
        num_p_b = connection.execute(sqlalchemy.text(num_potions_b)).scalar()
        num_mili_g = connection.execute(sqlalchemy.text(num_ml_g)).scalar()
        num_mili_r = connection.execute(sqlalchemy.text(num_ml_r)).scalar()
        num_mili_b = connection.execute(sqlalchemy.text(num_ml_b)).scalar()
        gold = connection.execute(sqlalchemy.text(gold_sql)).scalar()

        total_p = num_p_g + num_p_r + num_p_b
        total_ml = num_mili_g + num_mili_r + num_mili_b
    
    return {"number_of_potions": total_p, "ml_in_barrels": total_ml, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():

    num_potions_g = "SELECT num_green_potions FROM global_inventory"
    num_potions_b = "SELECT num_red_potions FROM global_inventory"
    num_potions_r = "SELECT num_blue_potions FROM global_inventory"
    num_ml_g = "SELECT num_green_ml FROM global_inventory"
    num_ml_r = "SELECT num_blue_ml FROM global_inventory"
    num_ml_b = "SELECT num_red_ml FROM global_inventory"
    gold_sql = "SELECT gold FROM global_inventory"
                        
    with db.engine.begin() as connection:
        num_p_g = connection.execute(sqlalchemy.text(num_potions_g)).scalar()
        num_p_r = connection.execute(sqlalchemy.text(num_potions_r)).scalar()
        num_p_b = connection.execute(sqlalchemy.text(num_potions_b)).scalar()
        num_mil_g = connection.execute(sqlalchemy.text(num_ml_g)).scalar()
        num_mil_r = connection.execute(sqlalchemy.text(num_ml_r)).scalar()
        num_mil_b = connection.execute(sqlalchemy.text(num_ml_b)).scalar()
        gold = connection.execute(sqlalchemy.text(gold_sql)).scalar()

        total_p = num_p_g + num_p_r + num_p_b
        total_ml = num_mil_g + num_mil_r + num_mil_b

        potion_cap = 0
        ml_cap = 0
    if gold >= 1000:
        if total_p < 10:
            potion_cap = 1
        if  total_ml < 100:
            ml_cap = 1
        with db.engine.begin() as connection:
            inventory_update = """UPDATE global_inventory SET
                                    num_red_potions = num_red_potions + :potion
                                    num_green_potions = num_green_potions + :potion
                                    num_blue_potions = num_blue_potions + :potion
                                    num_red_ml = num_red_ml + :ml
                                    num_green_ml = num_green_ml + :ml
                                    num_blue_ml = num_blue_ml + :ml"""
            gold_update = "UPDATE global_inventory SET gold = gold - (1000 * :ml_cap * :p_cap)"
            new_inventory = connection.execute(sqlalchemy.text(inventory_update), {"potion": int(potion_cap / 3), "ml": int(ml_cap / 3)})
            new_gold = connection.execute(sqlalchemy.text(gold_update), {"ml_cap": ml_cap, "p_cap": potion_cap})
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

    print(capacity_purchase.potion_capacity)
    print(capacity_purchase.ml_capacity)
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
