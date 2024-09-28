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
    
    return {"number_of_potions": 0, "ml_in_barrels": 0, "gold": 0}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    with db.engine.begin() as connection:
        sql_to_execute1 = "SELECT num_green_potions FROM global_inventory"
        result1 = connection.execute(sqlalchemy.text(sql_to_execute1))
        sql_to_execute1 = "SELECT num_green_ml FROM global_inventory"
        result2 = connection.execute(sqlalchemy.text(sql_to_execute2))
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
