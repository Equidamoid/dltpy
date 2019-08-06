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
find_package(Boost REQUIRED
    COMPONENTS
        python3
)
find_package(PythonLibs 3 REQUIRED)
find_package(fmt REQUIRED)
add_definitions('--std=c++17')
add_definitions('-Wall')
set(CMAKE_EXPORT_COMPILE_COMMANDS YES)

add_library(${PROJECT_NAME}
SHARED
    dltreader.cpp
    dltreader_boost.cpp
    log.cpp
)
target_include_directories(${PROJECT_NAME}
    PUBLIC 
    ${Boost_INCLUDE_DIRS} 
    ${PYTHON_INCLUDE_DIR}
)
target_link_libraries(${PROJECT_NAME}
    ${Boost_LIBRARIES}
    ${PYTHON_LIBRARY}
    fmt::fmt
)
set_target_properties(
    ${PROJECT_NAME}
    PROPERTIES
        PREFIX ""
        SUFFIX ".so"
        OUTPUT_NAME ${PROJECT_NAME}
        LINKER_LANGUAGE C
    )

