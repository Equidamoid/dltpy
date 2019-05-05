# Copyright (C) 2018, Vladimir Shapranov 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
project(native_dltfile)
find_package(Boost REQUIRED
    COMPONENTS
        python3
)
find_package(PythonLibs 3 REQUIRED)
add_definitions('--std=c++17')
add_library(${PROJECT_NAME}
SHARED
    dltfile.cpp
)

target_include_directories(${PROJECT_NAME}
    PUBLIC 
    ${Boost_INCLUDE_DIRS} 
    ${PYTHON_INCLUDE_DIR}
)
target_link_libraries(${PROJECT_NAME}
    ${Boost_LIBRARIES}
    ${PYTHON_LIBRARY}
)
set_target_properties(
    ${PROJECT_NAME}
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME ${PROJECT_NAME}
        LINKER_LANGUAGE C
    )

#install(TARGETS pythondecoderplugin DESTINATION deploy/plugins)
