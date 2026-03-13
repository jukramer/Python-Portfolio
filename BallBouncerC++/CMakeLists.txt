cmake_minimum_required(VERSION 3.16)

project(BouncingBall)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# Tell CMake where Qt is installed
set(CMAKE_PREFIX_PATH "C:/Qt/6.10.2/mingw_64")

find_package(Qt6 REQUIRED COMPONENTS Core)
find_package(Qt6 REQUIRED COMPONENTS Widgets)

add_executable(BouncingBall main.cpp entities.cpp qt.cpp)
target_include_directories(BouncingBall PRIVATE include/)

target_link_libraries(BouncingBall Qt6::Core)
target_link_libraries(BouncingBall Qt6::Widgets)