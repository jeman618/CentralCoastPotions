from fastapi import APIRouter
import sqlalchemy
from src import database as db
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():

    catalog_sql = "SELECT sku, name, inventory, potion_type, price FROM catalog"
    catalog_sql_1 = "SELECT sku FROM catalog"
    inventory_sql = "UPDATE catalog SET inventory = :inventory WHERE sku = :sku"

    with db.engine.begin() as connection:
        catalog_sku = connection.execute(sqlalchemy.text(catalog_sql_1)).fetchall()
        catalog_list = connection.execute(sqlalchemy.text(catalog_sql)).fetchall()

    potion_inventory = 0
    x = 0
    catalog = []
    with db.engine.begin() as connection:

        for item in catalog_list:

            potion_inventory = item[2]
            if (potion_inventory > 0):
                new_inventory = connection.execute(sqlalchemy.text(inventory_sql), {"inventory": potion_inventory, "sku": str(catalog_sku[x]) })
                catalog.append({"sku": item[0], "name": item[1], "quantity": potion_inventory,
                    "price": item[4], "potion_type": item[3],
                })
            x += 1  
        
    if len(catalog) == 0:
        print("no potions available")
        return []
    print(catalog)
    """
    Each unique item combination must have only a single price.
    """
    
    return catalog
        

