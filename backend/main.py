from cart_auto.carts import Cart
from cart_home.home import Home
from cart_cornall.corral import Corral
import numpy as np
import time
from database.mini_database import MiniBase
from utils import debug, reset_count, new_doc

address = "700 Boston Road Billerica, MA 01821"
database = MiniBase()

new_doc("Home")
home = Home(database=database,
            store="Market Basket", 
            address=address, 
            store_coordinates="42.558° N, 71.268° W", 
            carts_deploy_coordinates="41.8847° N, 87.6510° W")
database.add_to_home_minibase(home)
debug(f"store data: {home.data}")
new_doc("Cart A")
num1 = database.generate_number_database_size("cart")
cartA = Cart(Home=home, number=num1)
database.add_to_cart_minibase(cartA)
debug(f"New cart added: {cartA.number}\n")
time.sleep(1)

new_doc("Cart B")
num2 = database.generate_number_database_size("cart")
cartB = Cart(Home=home, number=num2)
database.add_to_cart_minibase(cartB)
debug(f"New cart added: {cartB.number}\n")
time.sleep(1)

new_doc("Corral A")
num3 = database.generate_number_database_size("corral")
corralA = Corral(database=database, home=home, number=num3)
database.add_to_corral_minibase(corralA)
debug(f"New corral added: {corralA.number}")
time.sleep(1)


new_doc("Corral B")
num4 = database.generate_number_database_size("corral")
corralB = Corral(number=num4, database=database, home=home)
database.add_to_corral_minibase(corralB)
debug(f"New corral added: {corralB.number}")
time.sleep(1)

new_doc("Adding carts to home and corral")
home.add_cart(cartA)
home.add_cart(cartB)
corralA.add_cart(cartA)
corralA.add_cart(cartB)
corralB.add_cart(cartA)
corralB.add_cart(cartB)
home.add_corral(corralA)
home.add_corral(corralB)
time.sleep(1)

print(f"info on home: {home}\n")
print(f"database: {database}")
