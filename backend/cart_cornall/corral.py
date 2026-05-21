# corral.py


import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cart_home.home import Home
    from cart_auto.carts import Cart

class Corral:
    
    """
    I suspect theyll be around 6-8 corral or each companies on average.
    
    corral legit wont do much, it's just for attracting the carts (especially outsiders), cart hoarding, and MAYBE be a "traffic Officer"
    """
    def __init__(self, 
                 database,
                 number:int,
                 home:"Home", 
                 stores_perferred_limit:int=30):
        breakdown = self.breakdown_home(home=home)
        self.database = database
        self.home = Home
        self.number = number # the number of the corral, example "corral 5 likes corral 3"
        self.store = breakdown["store"]  # Store name, can be set to any store
        self.address = breakdown["address"]
        self.homes_perferred_deploy = breakdown["preferred_spot"]
        self.full:bool = False
        self.max_carts_inside = stores_perferred_limit
        self.id = str(uuid.uuid4())
        self.current_storage_amount = 0
        self.cart_ids = []
        self.brothers_and_sisters:list[tuple[Corral, int]] = []
        self.last_to_join:"Cart"|None = None
        
    def inspection(self, cart:"Cart"):
        if self.full:
            lowest_distance = self.homes_perferred_deploy # distance of closest corral, defaults to stores deploy if none found
            found:bool = False # check if anything was found
            for corrals in self.brothers_and_sisters:
                corral = corrals[0]
                distance = corrals[1]
                
                if corral.full:
                    print(f"{corral.number} is full")
                    continue # skip if that corral is full
                
                # do math do calulate distance
                if distance < lowest_distance:
                    found = True # a corral was found
                    lowest_distance = distance # new lowest distance
            
            if found: # if found, go to that corral
                cart.go(lowest_distance)
            else: # if not, go to the store if close to it, else send a call
                if lowest_distance > 100: # if the distance is more than 100 feet, send a call for manual pick up
                    print("poor baby is lost, go pick them up!")
                    self.send_distress(cart)
                    return
                print("ALL CORRALS ARE FULL, JUST GO HOME")
                cart.go(lowest_distance)
            return
        
        self.add_cart(cart.id)
        
    def send_distress(self, cart:"Cart"):
        pass 
    
    def add_cart(self, cart_id:str):
        
        self.current_storage_amount += 1
        self.cart_ids.append(cart_id)
        cart = self.database.get_cart(cart_id)
        self.last_to_join = cart
        self.commit()
        
    def remove_cart(self,cart_id:str):
        self.current_storage_amount -= 1
        self.cart_ids.remove(cart_id)
        self.commit()
    
    def commit(self):
        pass
    
    def go_buddy(self):
        if not self.last_to_join:
            print("No carts detected")
            return
        self.last_to_join.go(self.homes_perferred_deploy)
         
    def add_other_corral(self, corral:"Corral"):
        distance = ... # TODO: distance of the corral
        self.brothers_and_sisters.append((corral, distance))
    
    def change_number(self, new_number:int):
        """Change the number of the corral, this might not be useful much but it's more for mistakes"""
        
        # TODO: add software where it returns null if a corral with that number already exists, but for now we will just ignore it and assume the user is smart enough to not do that
        if not new_number:
            return
        
        if new_number == self.number:
            return
        
        if new_number > 30:
            print("unless this is a super store, CartyGo doesn't believe you need that many corrals")
            return
        
        # for corrals in self.brothers_and_sisters:
        #     corral = corrals[0]
        #     if corral.number == new_number:
        #       print(f"Corral {new_number} already exists, please choose a different number")
        #       return
        
        print(f"corral {self.number} is now corral {new_number}")
        self.number = new_number
        
    def breakdown_home(self, home:"Home"):
        if not home:
            raise ValueError("Cart's home wasn't provided or is invalid.")
        if not home.store or not home.address:
            raise ValueError(f"Error finding home's info: store ({home.store if home.store else 'is null'}), address ({home.address if home.address else 'is null'})")
        return {"store":home.store, "address": home.address, "preferred_spot": home.preferred_deploy_coordinates}
    