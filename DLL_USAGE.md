# Autel Thermal Converter DLL - Python Usage Guide

This guide documents the API and usage of the `ir_converter.dll` (Shared Library) for converting Autel thermal JPG images into 16-bit TIFFs and extracting metadata.

## Overview

The DLL provides a high-performance C++ backend for:
1.  **Image Conversion**: Converting proprietary Autel thermal JPGs into 4-Channel 16-bit TIFF files.
2.  **Metadata Extraction**: Retrieving thermal statistics and sensor details as JSON.

## Temperature Encoding (Crucial)

The thermal data is encoded into **Band 4** of the output TIFF using a **Fixed-Point Offset** format to preserve decimal precision in a 16-bit integer container.

**Formula:**
$$ PixelValue = (Temperature°C \times 100) + 10000 $$

**Decoding Logic:**
To get the actual Celsius value back:
$$ Temperature°C = \frac{PixelValue - 10000}{100.0} $$

| Temperature | Encoded Pixel Value (uint16) |
|:-----------:|:----------------------------:|
| -20.00°C    | 8000                         |
| 0.00°C      | 10000                        |
| 23.45°C     | 12345                        |
| 150.00°C    | 25000                        |

---

## API Reference

### 1. `ConvertToTiff`

Converts a single JPG image to a 4-channel TIFF.

**C++ Signature:**
```cpp
int ConvertToTiff(const char* inputPath, const char* outputPath);
```

**Parameters:**
*   `inputPath`: Absolute or relative path to the source `.JPG`.
*   `outputPath`: Desired path for the output `.tif`.

**Return Values:**
*   `0`: Success.
*   `-1`: Failed to load input image (or file not found).
*   `-2`: SDK Error (Not a valid Autel thermal image).
*   `-3`: Failed to write output file.

### 2. `GetMetadataJSON`

Extracts thermal statistics and metadata into a JSON string.

**C++ Signature:**
```cpp
int GetMetadataJSON(const char* inputPath, char* buffer, int bufferLen);
```

**Parameters:**
*   `inputPath`: Path to the source `.JPG`.
*   `buffer`: A pointer to a char array to hold the output string.
*   `bufferLen`: The size of the allocated buffer (Recommended: 10KB / 10240 bytes).

**Return Values:**
*   `0`: Success.
*   `-1`: SDK Error / Parse failed.
*   `-2`: Buffer too small to hold the JSON string.

---

## Python Integration Example

Below is a minimal example of how to load and use the DLL using Python's built-in `ctypes` library.

### Prerequisites
*   Python 3.x
*   The `ir_converter.dll` must be in a known path.
*   The `AutelIrTempParserSDK.dll` and OpenCV DLLs must be in the same directory as `ir_converter.dll` or in the system PATH.

### Code Snippet

```python
import ctypes
import json
import os

# 1. Load the DLL
dll_path = "./build/Release/ir_converter.dll"
if not os.path.exists(dll_path):
    raise FileNotFoundError("DLL not found")

lib = ctypes.CDLL(dll_path)

# 2. Define Argument and Return Types (Best Practice)
lib.ConvertToTiff.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
lib.ConvertToTiff.restype = ctypes.c_int

lib.GetMetadataJSON.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
lib.GetMetadataJSON.restype = ctypes.c_int

# 3. Wrapper Functions
def convert_image(input_jpg, output_tif):
    # Strings must be encoded to bytes (utf-8) for C++
    b_in = input_jpg.encode('utf-8')
    b_out = output_tif.encode('utf-8')
    
    result = lib.ConvertToTiff(b_in, b_out)
    
    if result == 0:
        print(f"✅ Success: {output_tif}")
    else:
        print(f"❌ Error Code: {result}")

def get_metadata(input_jpg):
    b_in = input_jpg.encode('utf-8')
    
    # Allocate a buffer (10KB)
    buffer_size = 10240
    buffer = ctypes.create_string_buffer(buffer_size)
    
    result = lib.GetMetadataJSON(b_in, buffer, buffer_size)
    
    if result == 0:
        # Decode bytes back to string
        json_str = buffer.value.decode('utf-8')
        return json.loads(json_str)
    else:
        print(f"❌ Error getting metadata: {result}")
        return None

# 4. Usage
if __name__ == "__main__":
    src = "images/IRX_1234.JPG"
    dst = "output/IRX_1234.tif"
    
    # Create output dir if needed
    os.makedirs("output", exist_ok=True)
    
    # Run conversion
    convert_image(src, dst)
    
    # Get Data
    meta = get_metadata(src)
    if meta:
        print("Max Temp:", meta['stats']['max'])
        print("Min Temp:", meta['stats']['min'])
```

## JSON Output Structure

The `GetMetadataJSON` function returns data in the following structure:

```json
{
  "stats": {
    "min": 15.4,
    "max": 34.2,
    "avg": 22.1,
    "min_point": { "x": 100, "y": 200 },
    "max_point": { "x": 300, "y": 400 }
  },
  "metadata": {
    "IR_Emissivity": 100,
    "IR_ReflectedTemp": 230,
    "IR_Distance": 50,
    ... (other vendor specific tags)
  }
}
```
