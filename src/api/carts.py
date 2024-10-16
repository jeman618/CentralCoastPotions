from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(visit_id)
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    print(new_cart)
    """ """
    return {"cart_id": 1}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):

    cart = """INSERT INTO cart_items (cart_id, quantity, catalog_id)
              SELECT :cart_id, :quantity, catalog_id
              FROM catalog WHERE catalog.sku = :item_sku"""
    
    with db.engine.begin() as connection:
        new_cart = connection.execute(sqlalchemy.text(cart), {"cart_id": cart_id, "quantity": cart_item.quantity, "item_sku": item_sku})
    """ """
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    get_quantity = "SELECT quantity FROM cart_items WHERE cart_id = :cart_id"
    get_catalog_id = "SELECT cart_items.catalog_id FROM cart_items WHERE cart_id = :cart_id"
    get_price = """SELECT price 
                   FROM catalog
                   LEFT JOIN cart_items
                        ON catalog.catalog_id = cart_items.catalog_id
                   WHERE cart_items.cart_id = :cart_id"""
    
    with db.engine.begin() as connection:
        catalog_id = connection.execute(sqlalchemy.text(get_catalog_id), {"cart_id": cart_id}).scalar()
        price = connection.execute(sqlalchemy.text(get_price), {"cart_id": cart_id}).scalar()
        quantity = connection.execute(sqlalchemy.text(get_quantity),{"cart_id": cart_id}).scalar()

    payment = quantity * price
    num_potions_update = ""
    print(f"payment: {payment}")
    
    if(catalog_id == 1):
        num_potions_update = "UPDATE global_inventory SET num_red_potions = num_red_potions - :quantity"
    elif(catalog_id == 2):
        num_potions_update = "UPDATE global_inventory SET num_green_potions = num_green_potions - :quantity"
    elif(catalog_id == 3):
        num_potions_update = "UPDATE global_inventory SET num_blue_potions = num_blue_potions - :quantity"
    elif(catalog_id == 4):
        num_potions_update = "UPDATE global_inventory SET num_white_potions = num_white_potions - :quantity"

    gold_update = "UPDATE global_inventory SET gold = gold + :payment"
    remove_cart_sql = "DELETE FROM cart_items WHERE cart_id = :cart_id"
    inventory_update = """UPDATE catalog
                          SET inventory = inventory - cart_items.quantity
                          FROM cart_items
                          WHERE catalog.catalog_id = cart_items.catalog_id AND cart_items.cart_id = :cart_id"""
    with db.engine.begin() as connection:
        new_gold = connection.execute(sqlalchemy.text(gold_update), {"payment": payment})
        new_num_potions = connection.execute(sqlalchemy.text(num_potions_update), {"quantity": quantity})
        new_inventory = connection.execute(sqlalchemy.text(inventory_update), {"cart_id": cart_id})
        remove_cart = connection.execute(sqlalchemy.text(remove_cart_sql), {"cart_id": cart_id})

    return {"total_potions_bought": quantity, "total_gold_paid": payment}
