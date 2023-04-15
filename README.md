![logo](https://raw.githubusercontent.com/Viatorus/quom/master/artwork/logo_banner.png)

[![Build Status](https://github.com/Viatorus/quom/workflows/Testing/badge.svg)](https://github.com/viatorus/quom/actions)
[![PyPI](https://img.shields.io/pypi/v/quom.svg)](https://pypi.org/project/Quom/)


# Quom
Quom is a single file generator for C/C++.

It resolves all included local headers starting with your main C/C++ file. This is also known as amalgamation.

Afterwards, it tries to find the related source files and their headers and places them at the end of the main file
or at a specific stitch location if provided.

At the end there will be one single file with all your header and sources joined together.

## Installation

```
pip install --user quom
```

Requires Python 3.7 or later.

## How to use it

```
usage: quom [-h] [--stitch format] [--include_guard format] [--trim]
            input output

Single header generator for C/C++ libraries.

positional arguments:
  input                 Input file path of the main file.
  output                Output file path of the generated single header file.

optional arguments:
  -h, --help            show this help message and exit
  --stitch format, -s format
                        Format of the comment where the source files should be placed
                        (e.g. // ~> stitch <~). Default: None (at the end of the main file)
  --include_guard format, -g format
                        Regex format of the include guard. Default: None
  --trim, -t            Reduce continuous line breaks to one. Default: True
  --include_directory INCLUDE_DIRECTORY, -I INCLUDE_DIRECTORY
                        Add include directories for header files.
  --source_directory SOURCE_DIRECTORY, -S SOURCE_DIRECTORY
                        Set the source directories for source files.
                        Use ./ in front of a path to mark as relative to the header file.
  --encoding ENCODING, -e ENCODING
                        The encoding used to read and write all files.
```

## Simple example

The project:

```
|-src/
|  |-foo.hpp
|  |-foo.cpp
|   -main.cpp
|-out/
    -main_gen.cpp
```

*foo.hpp*

```cpp
#pragma once

int foo();
```

*foo.cpp*

```cpp
#include "foo.hpp"

int foo() {
    return 0;
}
```

*main.cpp*

```cpp
#include "foo.hpp"

int main() {
    return foo();
}
```

The command:

```
quom src/main.hpp main_gen.cpp
```

*main_gen.cpp*

```cpp
int foo();

int main() {
    return foo();
}

int foo() {
    return 0;
}
```

## Advanced example

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
#define FOOBAR_FOO_HPP

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
#define FOOBAR_HPP

#include "foo.hpp"

#endif

#ifdef FOO_MAIN

// ~> stitch <~

#endif
```

The command:

```
quom src/foobar.hpp foobar_gen.hpp -s "~> stitch <~" -g FOOBAR_.+_HPP
```

*foobar_gen.hpp*

```cpp
#pragma once

#ifndef FOOBAR_HPP
#define FOOBAR_HPP

extern int foo;

#endif

#ifdef FOO_MAIN

int foo = 42;

#endif
```

Take a look into the [examples folder](examples/) for more.
