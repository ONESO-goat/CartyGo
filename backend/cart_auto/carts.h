// carts.h
#ifndef CARTS_H
#define CARTS_H
#include <cartstate.h>
#include <cartspeed.h>
#include <string>
#include <vector>
#include <map>

 
    void calculatePressure(); 
    void addItem(std::string item);
    void moveForward(CartSpeed speed);
    void emergencyShutdown(bool reboot);
    void addNewCorral(std::string corralId);
    void changeAddress(std::string newAddress);
    void changeStore(std::string store);
    int getPreviousAddressesLength();
    void shutdown();
    std::string warning(std::string issue);
    void changeState(CartState newState);
    void searchNearestCorral();
    std::map<std::string, std::string> breakdownHome(Home home);
    void createJson();
    void saveJson();


#endif