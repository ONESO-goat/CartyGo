import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cart_auto.carts import Cart
    from cart_home.home import Home
    from cart_cornall.corral import Corral


class MiniBase:
    def __init__(self):
        # Initializing local collections inside the instance boundary
        self.cart_database: list[dict] = []
        self.home_database: list[dict] = []
        self.corral_database: list[dict] = []
    def generate_number_database_size(self,for_which_database:str):
        """Cart, Home, or Corral"""
        for_which_database = for_which_database.lower().strip()
        if for_which_database == "cart":
            
            return len(self.cart_database) + 1
        
        elif for_which_database == "home":
          
            return len(self.home_database) + 1

        elif for_which_database == "corral":
            
            return len(self.corral_database) + 1
        else: 
            raise ValueError(f"type not reconized: {for_which_database}")

    def add_to_cart_minibase(self, cart: "Cart") -> list[dict]:
        """Saves a snapshot profile of a cart state asset."""
        self.cart_database.append({
            "id": cart.id,
            "store_cart_id": cart.store_cart_id,
            "number": cart.number,
            "store": cart.store,
            "address": cart.address,
            "state": str(cart.state),
            "online": cart.online
        })
        return self.cart_database
        
    def add_to_corral_minibase(self, corral: "Corral") -> list[dict]:
        """Saves a snapshot profile of a corral collection target."""
        self.corral_database.append({
            "id": corral.id,
            "number": corral.number,
            "home_id": corral.home.id,
            "store": corral.store,
            "address": corral.address,
            "max_capacity": corral.max_carts_inside,
            # Extract just the sibling corral numbers/distances instead of raw objects
            "connected_siblings": [
                {"sibling_number": sib.number, "distance_ft": dist} 
                for sib, dist in corral.brothers_and_sisters
            ]
        })
        return self.corral_database

    def add_to_home_minibase(self, home: "Home") -> list[dict]:
        """Saves a snapshot profile of a master store base."""
        # We leverage the .data property layout we built into Home to keep things clean!
        self.home_database.append({
            "id": home.id,
            "store": home.store,
            "address": home.address,
            "coordinates": str(home.store_coordinates),
            "corrals": home.corrals,
            # Pull clean serialized string identifiers
            "carts": [cart.store_cart_id for cart in home.connected_carts]
        })
        return self.home_database
    
    @property
    def all_databases(self):
        """get all databases"""
        return {"home": self.home_database, "cart": self.cart_database, "corral": self.corral_database}
    
    def __str__(self):
        """Outputs a cleanly formatted, highly scannable JSON representation of your state."""
        # json.dumps converts our dictionaries into clean, pretty-printed text arrays
        home_pretty = json.dumps(self.home_database, indent=4)
        cart_pretty = json.dumps(self.cart_database, indent=4)
        corral_pretty = json.dumps(self.corral_database, indent=4)
        
        return (
            f"=========================================\n"
            f"DATABASE STATUS EXPORT\n"
            f"=========================================\n\n"
            f"🏠 Home Base Registry:\n{home_pretty}\n\n"
            f"🛒 Active Cart Registry:\n{cart_pretty}\n\n"
            f"🚧 Parking Corral Registry:\n{corral_pretty}"
        )