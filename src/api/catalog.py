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
    catalog_sql_1 = "UPDATE catalog SET inventory = inventory + :ml_r WHERE catalog_id = 1"
    catalog_sql_2 = "UPDATE catalog SET inventory = inventory + :ml_g WHERE catalog_id = 2"
    catalog_sql_3 = "UPDATE catalog SET inventory = inventory + :ml_b WHERE catalog_id = 3"
    
    with db.engine.begin() as connection:
        r_p = connection.execute(sqlalchemy.text(r_potions)).scalar()
        g_p = connection.execute(sqlalchemy.text(g_potions)).scalar()
        b_p = connection.execute(sqlalchemy.text(b_potions)).scalar()
        inventory_red = connection.execute(sqlalchemy.text(catalog_sql_1), {"ml_r": r_p})
        inventory_green = connection.execute(sqlalchemy.text(catalog_sql_2), {"ml_g": g_p})
        inventory_blue = connection.execute(sqlalchemy.text(catalog_sql_3), {"ml_b": b_p})

    catalog = []
    if r_p > 0:
        catalog.append({"sku": "RED", "name": "red potion", "quantity": r_p,
                "price": 50, "potion_type": [100, 0, 0, 0],
            })
    if g_p > 0:
        catalog.append({"sku": "GREEN", "name": "green potion", "quantity": g_p,
                "price": 40, "potion_type": [0, 100, 0, 0],
            })
    if b_p > 0:
        catalog.append({"sku": "BLUE", "name": "blue potion", "quantity": b_p,
                "price": 30, "potion_type": [0, 0, 100, 0],
            })
        
    
    if g_p == 0 and r_p == 0 and b_p == 0:
        print("no potions available")
        return []
    """
    Each unique item combination must have only a single price.
    """
    
    return catalog
        

