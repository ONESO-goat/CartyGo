# ai.py, I came up with the name "CartyGo" and already like it, this whole project/"business" will be named "CartyGo"

from .engine import Engine


class CartyGo(Engine):
    """The AI"""
    def __init__(self, Home, cart_id, address):
        super().__init__()
        pass
    
    def directions_to_follow(self, directions:str):
        super()._follow(directions)