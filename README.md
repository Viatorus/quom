![logo](https://raw.githubusercontent.com/Viatorus/quom/master/artwork/logo_banner.png)

![Travis](https://travis-ci.org/Viatorus/quom.svg?branch=master)
[![PyPI](https://img.shields.io/pypi/v/quom.svg)](https://pypi.org/project/Quom/)


# Quom
Quom is a single header generator for C/C++ libraries.

# Installation

```
pip install quom
```

Only **Python 3.6+** is supported.

# How it works

Quom resolves all local includes starting with the main header file of your library.

Afterwards, it tries to find the related source files and places them at the specific stitch location.

# How to use it 

```
usage: quom [-h] [--stitch format] [--include_guard format] [--trim]
            input output

Single header generator for C/C++ libraries.

positional arguments:
  input                 Input file path of the main header file.
  output                Output file path of the generated single header file.

optional arguments:
  -h, --help            show this help message and exit
  --stitch format, -s format
                        Format of the comment where the source files should be
                        placed. Default: ~> stitch <~
  --include_guard format, -g format
                        Regex format of the include guard. Default: None
  --trim, -t            Reduce continuous line breaks to one. Default: True
```

Take a look into the [examples folder](examples/) for more.

# Simple example

The project:

```
|-src/
|  |-foo.hpp
|  |-foo.cpp
|   -foobar.hpp
|-out/
    -foobar_gen.hpp

```

*foo.hpp*

```cpp
#pragma once

#ifndef FOOBAR_FOO_HPP
#endif FOOBAR_FOO_HPP

extern int foo; 

#endif
```

*foo.cpp*

```cpp
#include "foo.hpp"

int foo = 42;
```

*foobar.hpp*

```cpp
#pragma once

#ifndef FOOBAR_HPP
#endif FOOBAR_HPP

#include "foo.hpp"

#endif

#ifdef FOO_MAIN

// ~> stitch <~

#endif
```

The command:

```
quom src/foobar.hpp foobar_gen.hpp -g FOOBAR_.+_HPP
```

The result:

```cpp
#pragma once

#ifndef FOOBAR_HPP
#endif FOOBAR_HPP

extern int foo;

#endif

#ifdef FOO_MAIN

int foo = 42;

#endif
```
