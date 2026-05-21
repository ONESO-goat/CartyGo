from typing import Protocol

class NoneExistentCoordinates(Exception):
    pass

class Address(Protocol):
    def is_valid(self, address:str):
        pass
    

class Coordinates(Protocol):
    def is_valid(self, coordinates:str):
        pass


def get_cart(_id:str)->"Cart":
    from backend.cart_auto.carts import Cart
    pass

count = 1

def new_doc(what):
    l = len(what)*2
    print("="*l)
    print(f"{what}")
    print("="*l)
    
def debug(what):
    global count
    print(f"DEBUG {count}: \n\t\u2022{what}\n")
    count+=1
    
def reset_count():
    global count
    count=0
    
if __name__ == "__main__":
    debug("I LOVE CHEESE")
    l = [1,2,3,4,5]
    debug(l)