cmake_minimum_required(VERSION 3.20)
project(AutelIrToTiff)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 👇 FIND OPENCV — must come BEFORE add_executable
# Point OpenCV_DIR to the directory containing OpenCVConfig.cmake
find_package(OpenCV REQUIRED)

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/include ${OpenCV_INCLUDE_DIRS})

# 👇 DEFINE TARGET FIRST
add_executable(batch_ir2tif src/batch_ir2tif.cpp)

# 👇 NOW you can set properties on the target
if(MSVC)
    # Optional: only if you had issues with std::byte (usually not needed)
    # target_compile_definitions(batch_ir2tif PRIVATE _HAS_STD_BYTE=0)
endif()

# Link libraries
target_link_libraries(batch_ir2tif 
    ${CMAKE_SOURCE_DIR}/lib/AutelIrTempParserSDK.lib
    ${OpenCV_LIBS}
)

# Copy Autel SDK DLL
add_custom_command(TARGET batch_ir2tif POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_SOURCE_DIR}/bin/AutelIrTempParserSDK.dll
        $<TARGET_FILE_DIR:batch_ir2tif>
    COMMENT "Copying Autel SDK DLL"
)

# Copy OpenCV DLL (adjust version/path if needed)
add_custom_command(TARGET batch_ir2tif POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "C:/opencv/build/x64/vc16/bin/opencv_world4120.dll"
        $<TARGET_FILE_DIR:batch_ir2tif>
    COMMENT "Copying OpenCV DLL"
)

# Copy exiftool.exe if present
if(EXISTS ${CMAKE_SOURCE_DIR}/tools/exiftool.exe)
    add_custom_command(TARGET batch_ir2tif POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            ${CMAKE_SOURCE_DIR}/tools/exiftool.exe
            $<TARGET_FILE_DIR:batch_ir2tif>
        COMMENT "Copying exiftool.exe"
    )
endif()