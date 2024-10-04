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
    num_potions_sql = "SELECT num_green_potions FROM global_inventory"
    num_green_ml_sql = "SELECT num_green_ml FROM global_inventory"
    gold_sql = "SELECT gold FROM global_inventory"
                        
    with db.engine.begin() as connection:
        num_potions = connection.execute(sqlalchemy.text(num_potions_sql)).scalar()
        num_green_ml = connection.execute(sqlalchemy.text(num_green_ml_sql)).scalar()
        gold = connection.execute(sqlalchemy.text(gold_sql)).scalar()
    
    return {"number_of_potions": num_potions, "ml_in_barrels": num_green_ml, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():

    sql_to_execute1 = "SELECT num_green_potions FROM global_inventory"
    sql_to_execute2 = "SELECT num_green_ml FROM global_inventory"
    with db.engine.begin() as connection:
        result1 = connection.execute(sqlalchemy.text(sql_to_execute1)).scalar()
        result2 = connection.execute(sqlalchemy.text(sql_to_execute2)).scalar()
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": result1,
        "ml_capacity": result2
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
