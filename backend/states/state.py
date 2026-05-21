from enum import Enum
from prompts import CORRAL, CART, HOME
class CartState(Enum):
    BUSY = "busy" # force stop
    IDLE = "idle"           # at home
    DEPLOYED = "deployed"   # in store/lot
    RETURNING = "returning" # navigating home
    BLOCKED = "blocked"     # obstacle detected
    EMERGENCY = "emergency" # force stop
    
class CartSpeed(Enum):
    TARGET_SPEED = 5.5
    MINIMUM_SPEED = 1.5
    MAXIMUM_SPEED = 15
    STOP = 0
    CAUTION = 2
    
class Prompts(Enum):
    CARTS_PROMPT = CART,
    HOME_PROMPT = HOME,
    CORRAL_PROMPT = CORRAL
    

        
    