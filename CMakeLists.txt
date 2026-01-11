cmake_minimum_required(VERSION 3.20)
project(AutelIrToTiff)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 👇 FIND OPENCV — must come BEFORE add_executable
# Point OpenCV_DIR to the directory containing OpenCVConfig.cmake
find_package(OpenCV REQUIRED)

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/include ${OpenCV_INCLUDE_DIRS})

# 👇 DEFINE TARGET (SHARED LIBRARY)
add_library(ir_converter SHARED src/lib_ir_converter.cpp)

# 👇 NOW you can set properties on the target
if(MSVC)
    # Optional: only if you had issues with std::byte (usually not needed)
    # target_compile_definitions(ir_converter PRIVATE _HAS_STD_BYTE=0)
endif()

# Link libraries
target_link_libraries(ir_converter 
    ${CMAKE_SOURCE_DIR}/lib/AutelIrTempParserSDK.lib
    ${OpenCV_LIBS}
)

# Copy Autel SDK DLL to output
add_custom_command(TARGET ir_converter POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_SOURCE_DIR}/bin/AutelIrTempParserSDK.dll
        $<TARGET_FILE_DIR:ir_converter>
    COMMENT "Copying Autel SDK DLL"
)

# Copy OpenCV DLL (adjust version/path if needed)
add_custom_command(TARGET ir_converter POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "C:/opencv/build/x64/vc16/bin/opencv_world4120.dll"
        $<TARGET_FILE_DIR:ir_converter>
    COMMENT "Copying OpenCV DLL"
)