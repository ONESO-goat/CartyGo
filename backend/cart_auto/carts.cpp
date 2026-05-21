#include <string>
#include <iostream>
#include <vector>
using namespace std;


class Carts{
    public:
        long Id;
        string store;
        vector<string> items;
        int amountOfItems;
        string address;
        Carts(long id, string store, string address){
            this->Id = id;
            this->store = store;
            this->amountOfItems = 0;
        }
}