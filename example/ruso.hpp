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

#define

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

void call();

#include <iostream>

void call() {
    std::cout << "called" << std::endl;
}

Def::Def() {
	call();
}

#endif /* RUSO_MAIN */
