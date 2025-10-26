cmake_minimum_required(VERSION 3.20)
project(AutelIrToTiff)

set(CMAKE_CXX_STANDARD 17)

# Find OpenCV
find_package(OpenCV REQUIRED)

# Include SDK headers
include_directories(include ${OpenCV_INCLUDE_DIRS})

# Executable
add_executable(batch_ir2tif src/batch_ir2tif.cpp)

# Link libraries
target_link_libraries(batch_ir2tif 
    ${CMAKE_SOURCE_DIR}/lib/AutelIrTempParserSDK.lib
    ${OpenCV_LIBS}
)

# Copy your SDK DLL
add_custom_command(TARGET batch_ir2tif POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_SOURCE_DIR}/bin/AutelIrTempParserSDK.dll
        $<TARGET_FILE_DIR:batch_ir2tif>
)

# Copy OpenCV world DLL (Release version)
add_custom_command(TARGET batch_ir2tif POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "C:/opencv/build/x64/vc16/bin/opencv_world4120.dll"
        $<TARGET_FILE_DIR:batch_ir2tif>
    COMMENT "Copying OpenCV world DLL"
)