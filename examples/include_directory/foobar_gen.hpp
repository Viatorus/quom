#pragma once

#ifndef FOOBAR_HPP
#define FOOBAR_HPP

class Base {
public:
    Base();
};

class Foo : Base {
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

#endif // FOOBAR_HPP

#ifdef FOOBAR_MAIN

#include <iostream>

/* hello */
Base::Base() {
    std::cout << "Base constructed" << std::endl;
}

Abc::Abc() {
}

void call();

Def::Def() {
	call();
}

#include <iostream>

void call() {
    std::cout << "called" << std::endl;
}

#endif /* FOOBAR_MAIN */
