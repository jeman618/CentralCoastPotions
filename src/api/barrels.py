from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """    
    red = 0
    green = 0
    blue = 0
    dark = 0
    total_price = 0

    for barrel_delivered in barrels_delivered:
          total_price += (barrel_delivered.price * barrel_delivered.quantity)

          red += barrel_delivered.potion_type[0] * barrel_delivered.quantity * barrel_delivered.ml_per_barrel
          green += barrel_delivered.potion_type[1] * barrel_delivered.quantity * barrel_delivered.ml_per_barrel
          blue += barrel_delivered.potion_type[2] * barrel_delivered.quantity * barrel_delivered.ml_per_barrel
          dark += barrel_delivered.potion_type[3] * barrel_delivered.quantity * barrel_delivered.ml_per_barrel
        
    update_sql = """UPDATE global_inventory SET red_ml = red_ml + :red,
                                            green_ml = green_ml + :green,
                                            blue_ml = blue_ml + :blue,
                                            dark_ml = dark_ml + :dark,
                                            gold = gold - :payment"""
    
    print(total_price)
    with db.engine.begin() as connection:
        update = connection.execute(sqlalchemy.text(update_sql), 
                                    {"red": red, "green": green, "blue": blue, "dark": dark, "payment": total_price})

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]): 

    gold_SQL = "SELECT gold FROM global_inventory"
    types_SQL = "SELECT potion_type FROM catalog"
    ml_SQL = "SELECT red_ml, green_ml, blue_ml, dark_ml FROM global_inventory"
    p_inventory_SQL = "SELECT SUM(inventory) FROM catalog"

    with db.engine.begin() as connection:
                gold = connection.execute(sqlalchemy.text(gold_SQL)).scalar()
                potion_inventory = connection.execute(sqlalchemy.text(p_inventory_SQL)).scalar()
                ml = connection.execute(sqlalchemy.text(ml_SQL)).fetchone()

    ml = list(ml)
    print(ml)
    gold_amount = gold
    plan = []
    total_price = 0

    if(potion_inventory < 10):
        for barrel in wholesale_catalog:
            print(barrel)
            if (gold_amount - (barrel.price * barrel.quantity) > 0):
                    
                    total_price += (barrel.price * barrel.quantity)
                    gold_amount -= total_price
                    if (min(ml) == ml[3] and barrel.potion_type == [0,0,0,1]):
                        ml[3] += barrel.ml_per_barrel
                    elif (min(ml) == ml[2] and barrel.potion_type == [0,0,1,0]):
                        ml[2] += barrel.ml_per_barrel
                    elif (min(ml) == ml[1] and barrel.potion_type == [0,1,0,0]):
                        ml[1] += barrel.ml_per_barrel
                    elif (min(ml) == ml[0] and barrel.potion_type == [1,0,0,0]):
                        ml[0] += barrel.ml_per_barrel
                    else:
                        ml[0] += barrel.ml_per_barrel 

                    plan.append({"sku": barrel.sku,
                                "ml_per_barrel": barrel.ml_per_barrel,
                                "potion_type": barrel.potion_type,
                                "quantity": barrel.quantity,
                                "price": barrel.price})
                                
    print(f"Total gold paid: {total_price}")
    print(plan)
    return plan
        
    


