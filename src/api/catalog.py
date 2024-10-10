from fastapi import APIRouter
import sqlalchemy
from src import database as db
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():

    g_potions = "SELECT num_green_potions FROM global_inventory"
    r_potions = "SELECT num_red_potions FROM global_inventory"
    b_potions = "SELECT num_blue_potions FROM global_inventory"
    with db.engine.begin() as connection:
        g_p = connection.execute(sqlalchemy.text(g_potions)).scalar()
        r_p = connection.execute(sqlalchemy.text(r_potions)).scalar()
        b_p = connection.execute(sqlalchemy.text(b_potions)).scalar()

    catalog = []
    if g_p > 0:
        catalog.append({"sku": "RED_POTION_0", "name": "red potion", "quantity": g_p,
                "price": 50, "potion_type": [100, 0, 0],
            })
    if r_p > 0:
        catalog.append({"sku": "GREEN_POTION_0", "name": "green potion", "quantity": r_p,
                "price": 50, "potion_type": [0, 100, 0],
            })
    if b_p > 0:
        catalog.append({"sku": "BLUE_POTION_0", "name": "blue potion", "quantity": b_p,
                "price": 50, "potion_type": [0, 0, 100],
            })
    if g_p == 0 and r_p == 0 and b_p == 0:
        print("no potions available")
        return []
    """
    Each unique item combination must have only a single price.
    """
    
    return catalog
        

