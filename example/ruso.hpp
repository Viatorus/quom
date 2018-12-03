#ifndef RUSH_HPP
#define RUSH_HPP

class Base {
public:
    Base();
};

class Abc : Base {
public:
    Abc();
};

#define none

class Def : Base {
public:
    Def();
};

void start() {
    Abc abc;
    Def def;
}

#endif // RUSH_HPP

#ifdef RUSO_MAIN

#include <iostream>

/* hello */
Base::Base() {
    std::cout << "Base constructed" << std::endl;
}

Abc::Abc() {
}

