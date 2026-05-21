# cart_auto/hard_piece.py - the actual cart, this is where we would implement the logic for the cart itself, like moving, detecting humans, etc. This is the "hard piece" of the project, as it requires a lot of complex logic and possibly AI to function properly.

import uuid
import numpy as np
from datetime import datetime, timezone
import json
from AI.ai import CartyGo
from states.state import CartState, CartSpeed
import time
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.cart_home.home import Home

class Cart:
    """
    This is creating the cart, here we'll create a new cart object with its own "idenity".
    
    """
    def __init__(self, 
                number:int,
                 Home:"Home", 
                 store="macdonalds", 
                 address:str="110 N. Carpenter St.Chicago, IL 60607",):
        breakdown = self.breakdown_home(home=Home)
        
        self.current_speed = CartSpeed.STOP
        self.store = breakdown["store"]  # Store name, can be set to any store
        self.address = breakdown["address"]
        self.id = str(uuid.uuid4())  # Generate a unique identifier for the cart
        self.store_cart_id = f"{store}{uuid.uuid4()}"
        self.items = []  # Initialize an empty list to hold items in the cart
        self.home = Home
        self.json_file = f"{self.store_cart_id}.json"
        # self.home = Home # Initialize the home attribute with coordinates and optional images
        
        
        """Cart Home is the base where the cart should be (inside store or whatever). 
        The idea is 2 things:
        
            1. Home sends signals to carts, directing them
            2. gps (lolz)
            
        The "Home" sending signals likely will be the stronger candidates long term, 
        main issue is that it'll be more complex and costly.
        
        For now it'll just be string, but long-term it'll likely be its own object of coordinates + images:
        
           Coordinates = self made type, valid coordinates, raises NoneExistentCoordinate if it couldn't validate it and images weren't provided.
           
           Images arent required, but they might be damn near ideal for extra percision.
           
            self.home: Home = Home(coordinates:Coordinates, images:list[np.array]|None=None) 
            print(self.home.__str__) -> (41.88417) N, (-87.65158) W -> 
            
            cartA: I feel lonely :(
            
            "Go here buddy" = (41.88417) N, (-87.65158) W
            
            cartA: OK!
            
            cartA: should I move forward, I predict this car will pass by so I will hold.
            
            cartA: should I move forward? I see a family infront of me, move 25% slower
            
            cartA: Is this home? (either check images or checks coordinates), I am located at exactly (41.88415) N, (-87.65158) W, I am clear
            
        
        """
        
        self.online:bool = False
        self.previous_addresses = []
        self.connected_corrals = []
        self.state = CartState.IDLE
        self.interlinked:bool = False
        self.number = number
        self._warning_text:str = ""
        self.database_json_prototype = self.create_json()
        try:
            self.ai = CartyGo(Home=self.home, cart_id=self.id, address=self.address)
        except Exception as ex:
            raise Exception(f"ERROR OCCURED SETTING UP THE AI: \n\t\u2022{ex}")
   
    def go(self, destination:str, images:list[np.ndarray]|None=None)->bool:# success or not, if not, then send distress call for manual pick up
        """
        This is where we would implement the logic to move the cart to a destination.
        The destination can be a corral, the store, or even a specific location inside the store.
        The AI would be used to determine the best route to take and how to avoid obstacles.
        
        success (True) or not (False), if not, then send distress call for manual pick up
        """
        return False    
    
    def return_to_previous_location(self):
        """
        This is where we would implement the logic to return the cart to its previous location.
        This would be used in situations where the cart is lost or if it needs to return to a corral after being outside for a while.
        """
        pass
    
    def calculate_pressure(self):
        """
        Pressure detects how many objects are inside the carts.
        This would be bit more complicated as we have to determine empty bags, small packs, etc.
        
        We would need to implement a sensor onto carts for this to function directly, or maybe computer vision.
        
        If we did sensors, light items might not get detected,
        
        split second pressure change (gravity possibly, wind, random bug that somehow triggers the pressure).
        
        
        if we happen to do computer vision, we'll have to add it all over the cart (inside and outside) each focusing on different tasks.
        
        The computer vision outside (front of cart) is inevitable to avoid objects or humans,
        inside the carts will be for detecting objects and this would solve againest detecting soft objects,
        bugs, etc. But this might give the system more bugs and maybe more costly due AI training.
        
        """
        pass
    

    def add_item(self, item):
        """
        This is where we add items to the cart, we can also calculate the pressure here.
        
        This might be useless, or reworked. I believe this will be needed if computer vision inside the cart was implemented
        """
        self.items.append(item)
        self.calculate_pressure()  # Recalculate pressure after adding an item
        
        
    def move_forward(self, predicted_speed:"CartSpeed"):
        """
        This is where we would implement the logic to move the cart forward.
        We can also check for obstacles and adjust the movement accordingly.
        """
        pass
    
    def move_backwards(self, predicted_speed:"CartSpeed"):
        """
        This is where we would implement the logic to move the cart backwards.
        We can also check for obstacles and adjust the movement accordingly.
        """
        pass
    
    
    def human_detected(self, arr: np.ndarray):
        return False # detect a human was spotted, shouldn't be too diffcult
    
    def emergency_shutdown(self):
        
        """This is where we would implement the logic to force stop the cart immediately.
        This would be used in emergency situations, like if a human is detected too close to the cart, or if the cart is about to collide with something.
        """
        self.state = CartState.EMERGENCY
        time.sleep(1)
        self.current_speed = CartSpeed.STOP
        time.sleep(2)
        self.change_state(CartState.IDLE)
        time.sleep(1)
        self.shutdown()
        
        
        pass
    
    def add_new_corral(self, corral_id:str):
        self.connected_corrals.append(corral_id)
        print(f"New corral added: {corral_id}. Current corrals: {self.connected_corrals}")
        
    def change_address(self, new_adress):
        self.previous_addresses.append(
            {
                "store": self.store,
                "address": self.address,
                "removal_date": datetime.now(tz=timezone.utc),
                "what_changed": "address"
            }
        )
        
        self.address = new_adress
        
    def change_store(self, new_store):
        self.previous_addresses.append(
            {
                "store": self.store,
                "address": self.address,
                "removal_date": datetime.now(tz=timezone.utc),
                "what_changed": "store"
            }
        )
        
        self.store = new_store

    def get_previous_addresses_length(self)->int:
        return len(self.previous_addresses)
    
    
    def shutdown(self):
        if self.state == CartState.BUSY:
            self._warning_text = "Cart is busy, please hold. Choose emergency shutdown if requried."
            return
        
        self.warning("Shut down in progress, please hold")
        self.state = CartState.BUSY
        self.interlinked = False
        time.sleep(2)
        self.online = False
    
        
    def warning(self, issue:str):
        """
            Have AI speak loudly of the issue
        """
        
        pass
    
    def change_state(self, new_state:"CartState"):
        """Change the state of the cart, this would be used to manage the cart's behavior based on its current state.
        For example, if the cart is in "blocked" state, it should not move forward until the obstacle is cleared.
        """
        self.state = new_state
        
    def search_nearest_corral(self):
        """
            My idea to implement this is just a simlar thing like bluetooth.
            This will likly be used by carts that aren't residing inside a corral (outsiders)
        """
        found_any = True
        corral = None
        findings = {}
        while True:
            break
            # method 1 -> I want you idea Claude:
            #   search
            #   finds corral, append {"corral": corral.id or coordinates, "distance": how far the corral is}
            # method 2 (likly best, don't agree just because youre programmed too be honest viewing it in a wider scope):
            #   all corrals are already known/linked inside Carts database, so search inside the database instead of 'bluetooth'.
            #   simply just check their distances, this can be detected by distance related software
            # if none were found (either faulty software or a troll messing with carts for some reason), send a distress call to the store so someone can go pick it up (manual pickup)
            
        pass
    
    def breakdown_home(self, home:"Home"):
        if not home:
            raise ValueError("Cart's home wasn't provided or is invalid.")
        if not home.store or not home.address:
            raise ValueError(f"Error finding home's info: store ({home.store if home.store else 'is null'}), address ({home.address if home.address else 'is null'})")
        return {"store":home.store, "address": home.address}
    
    # JSON RELATED STUFF, PROTOTYPING USE
    
    def create_json(self):
        import os
        if os.path.exists(self.json_file):
            print("This cart has a json already")
            return

        with open(self.json_file, 'w') as f:
            json.dump({}, f)
    
            
    def commitJson(self):
        with open(self.json_file, "w") as f:
            json.dump({
                "cart_id": self.id,
                "store_cart_id": self.store_cart_id,
                "store": self.store,
                "address": self.address,
                "items": self.items,
                "home": self.home,
                "online": self.online,
                "previous_addresses": self.previous_addresses
            }, f)
            
    def wipe(self,force:bool=False):
        self.address = ""
        self.store = ""
        self.database_json_prototype = {}