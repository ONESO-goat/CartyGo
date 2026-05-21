#ifndef CARTSTATE_H
#define CARTSTATE_H

enum class CartState{
    BUSY, // force stop
    IDLE,          // at home
    DEPLOYED,  // in store
    RETURNING, // navigating home
    BLOCKED,// obstacle detected
    EMERGENCY, // force stop
    STOLEN,
    ATTACKED
};

#endif