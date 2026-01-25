# Autel Thermal Converter - User Guide

This package allows you to convert Autel thermal JPG images into analysis-ready TIFF files and extract temperature metadata using the Autel SDK.

## 1. Prerequisites

*   **Operating System:** Windows 10/11 (Required for the Autel SDK DLLs).
*   **Python:** Python 3.8 or newer.

## 2. Installation

1.  Open your terminal (PowerShell or Command Prompt).
2.  Navigate to the project root directory (where `setup.py` is located).
3.  Install the package using pip:

    ```bash
    pip install .
    ```

    *Note: This ensures all dependencies and internal DLLs are correctly registered.*

## 3. Command Line Interface (CLI)

After installation, the `autel-convert` command is available system-wide.

### Convert a Single Image
```bash
autel-convert "path/to/image.JPG" "path/to/output_folder"
```

### Convert an Entire Folder
Automatically finds and converts all JPG images in a folder.
```bash
autel-convert "path/to/source_folder" "path/to/output_folder"
```

**What you get:**
*   **`.tif` Files:** The converted images.
*   **`.json` Files:** (Single mode) Metadata for that image.
*   **`dataset_metadata.json`:** (Folder mode) A single file containing metadata for all processed images.

## 4. Python API Usage

You can use the converter directly in your own Python scripts.

```python
from autel_thermal_converter import ThermalConverter
import json

# 1. Initialize the converter
try:
    converter = ThermalConverter()
except Exception as e:
    print(f"Error loading converter: {e}")
    exit(1)

input_file = "DSC0001.JPG"
output_file = "DSC0001.tif"

# 2. Convert Image
# Returns True on success, False on failure
if converter.convert_image(input_file, output_file):
    print(f"Successfully created {output_file}")

# 3. Extract Metadata
# Returns a dictionary or None
metadata = converter.get_metadata(input_file)

if metadata:
    # Example: Accessing temperature stats
    stats = metadata.get('stats', {})
    print(f"Temperature Range: {stats.get('min')}°C to {stats.get('max')}°C")
    
    # Save to JSON if needed
    with open("metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)
```

## 5. Output Format Details

### The TIFF File
The output is a **4-Channel 16-bit Unsigned Integer** TIFF.

*   **Band 1-3:** RGB Channels (Scaled to 16-bit range).
*   **Band 4:** Thermal Data.

### Decoding Temperature (Band 4)
The thermal band does not store raw Celsius values directly (since TIFFs prefer integers). Instead, it uses a fixed-point encoding:

**Formula:**
$$ Temperature (°C) = \frac{PixelValue - 10000}{100.0} $$

**Examples:**
*   Pixel Value `10000` = `0.00 °C`
*   Pixel Value `12550` = `25.50 °C`
*   Pixel Value `8000`  = `-20.00 °C`

## Troubleshooting

### "DLL load failed" or "Module not found"
*   **Cause:** The application cannot find the required DLLs (`ir_converter.dll`, `AutelIrTempParserSDK.dll`, `opencv_world4120.dll`).
*   **Solution:**
    *   Ensure you are on **Windows**.
    *   Ensure you installed via `pip install .`. This sets up the paths correctly.
    *   If running from source without installing, ensure the `libs` folder is in your system PATH or properly referenced.

### "SDK Error"
*   **Cause:** The input JPG is not a valid Autel thermal image or is corrupted.
*   **Solution:** Check the file integrity. Ensure it was taken with a supported Autel thermal camera.
