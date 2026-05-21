# cart_home/home.py

import numpy as np
import uuid
import time
from utils import NoneExistentCoordinates, Address, Coordinates
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.cart_auto.carts import Cart
    from backend.cart_cornall.corral import Corral
class Home:
    """This is bascally the store it self, example this would be market basket.
    
    
    """
    def __init__(self, 
                 database,
                 store:str,
                 address:Address|str,
                 store_coordinates: Coordinates|str,
                 carts_deploy_coordinates: Coordinates|str, 
                 images:list[np.ndarray]|None=None):
        
        self.id = str(uuid.uuid4())
        self.database = database
        self.connected_carts = []
        self.corrals = []
        self.store_coordinates = store_coordinates
        self.preferred_deploy_coordinates = carts_deploy_coordinates
        self.address = address
        self.store = store
        
        
    def add_cart(self, cart: "Cart"):
        """Interlinks a fresh cart to the storefront grid system."""
        try:
            if not cart:
                return 
                
            cart.interlinked = True
            cart.online = True # Keep it awake and responsive upon setup
            
            if cart not in self.connected_carts:
                self.connected_carts.append(cart)
                
            cart.commitJson()
            print(f"Successfully interlinked Cart {cart.number} to base.")
            
        except Exception as ex:
            print(f"There was an error adding new cart: {ex}")
            return
        
    def validate_coordinates(self, coordinates):
        """Likly just use gemini to search if the address exist, is a store, has carts, etc"""
        
        raise NoneExistentCoordinates(f"Could not found coordinates: '{coordinates}'")

    def remove_cart(self, cart: "Cart"):
        """Safely severs connection, usually for decommissioning or repairs."""
        try:
            if not cart:
                return 
                
            cart.interlinked = False
            if cart in self.connected_carts:
                self.connected_carts.remove(cart)
                
            cart.commitJson()
            print(f"Removed connection for Cart {cart.number}.")
            cart.shutdown() # Safe to turn off now since it's leaving the active fleet
            
        except Exception as ex:
            print(f"There was an error removing cart: {ex}")
            return
        
        
    
    @property
    def data(self) -> dict:
        return {
            "store": self.store,
            "address": self.address,
            "coordinates":self.store_coordinates,
            "carts": [cart.id for cart in self.connected_carts],
            "corrals": self.corrals
        } 
        
    def add_corral(self, corral: "Corral"):
        """Registers a physical parking corral into the home tracking map."""
        if not corral:
            return
        
        # Avoid duplicate trackings
        if not any(c["id"] == corral.id for c in self.corrals):
            self.corrals.append({
                "id": corral.id,
                "number": corral.number,
                "max_capacity": corral.max_carts_inside
            })
            print(f"Registered Corral {corral.number} to store fleet.")
    
    def send_signal(self, cart: "Cart", signal: str):
        """Dispatches commands directly to individual automated carts."""
        print(f"[SIGNAL] Home base sending '{signal}' to Cart {cart.number}")
        # When your AI states are ready, this will fire: cart.change_state(signal)
        pass
    
    def __str__(self) -> str:
        return f"{self.store_coordinates}"