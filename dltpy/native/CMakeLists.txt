# Copyright (C) 2019, Vladimir Shapranov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

project(native_dltreader)
cmake_minimum_required(VERSION 3.10)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_EXTENSIONS OFF)
#set(CMAKE_CXX_CLANG_TIDY clang-tidy
#	-checks=-*,cppcoreguidelines-*,portability-*,bugprone-*)

add_subdirectory(pybind11)

#find_package(PythonLibs 3 REQUIRED)
find_package(fmt REQUIRED)
#add_definitions(-Wall -Wextra -pedantic -ansi)
set(CMAKE_EXPORT_COMPILE_COMMANDS YES)


add_library(dltreader_native SHARED
    dltreader_native.cpp
    dltreader.cpp
    log.cpp
    )


target_include_directories(dltreader_native
    PUBLIC
    ${PYTHON_INCLUDE_DIR}
)
target_link_libraries(dltreader_native
    ${PYTHON_LIBRARY}
    fmt::fmt
    pybind11::pybind11
)
set_target_properties(
    dltreader_native
    PROPERTIES
        PREFIX ""
        SUFFIX ".so"
        OUTPUT_NAME dltreader_native
        LINKER_LANGUAGE C
    )
