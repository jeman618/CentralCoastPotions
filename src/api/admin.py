from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():

    reset_potions_sql = "UPDATE catalog SET inventory = 0"
    reset_gl_sql = """UPDATE global_inventory SET gold = 100,
                                                red_ml = 0,
                                                green_ml = 0,
                                                blue_ml = 0,
                                                dark_ml = 0"""
    reset_cart_sql = "DELETE * FROM cart"
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(reset_potions_sql))
        connection.execute(sqlalchemy.text(reset_gl_sql))
        connection.execute(sqlalchemy.text(reset_cart_sql))
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    return "OK"


