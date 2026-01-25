# Autel Thermal Image Converter (Python + DLL)

A high-performance tool to convert Autel thermal JPG images (from EVO II Dual, Dragonfish, etc.) into 4-channel 16-bit TIFFs with embedded temperature data.

This project wraps the official Autel `IrTempParser` SDK in a C++ Shared Library (`.dll`) and provides a Python interface for batch processing.

---
## 📂 Project Structure

*   `thermal_converter.py`: **Main Entry Point**. Python script to convert images using the DLL.
*   `src/lib_ir_converter.cpp`: C++ source code for `ir_converter.dll`.
*   `include/`: Header files for the Autel SDK.
*   `old_files/`: Legacy tools (GUI, standalone EXE, ExifTool scripts) that are no longer supported in the main workflow.

## 🚀 Features

*   **Hybrid 4-Channel TIFF**:
    *   **Bands 1-3**: RGB Visual Data (Scaled to 16-bit).
    *   **Band 4**: Encoded Thermal Data (Fixed-Point format).
*   **Precision**: Preserves temperature data with 0.01°C precision using integer encoding.
*   **Metadata**: Extracts thermal statistics (Min/Max/Avg) and sensor metadata to JSON.
*   **Performance**: C++ core for fast image processing, Python for ease of use.
*   **Batch Processing**: Convert single files or entire folders.

---
## 🛠️ Requirements

*   **OS**: Windows 10/11 (64-bit)
*   **Python**: 3.8+
*   **Input**: Autel Thermal JPGs (`640x512` resolution recommended).

---
## 📦 Installation & Build

### 1. Prerequisites
*   CMake 3.20+
*   Visual Studio 2019/2022 (C++ Desktop Development)
*   OpenCV installed (e.g., `C:/opencv`)

### 2. Build the DLL
```powershell
mkdir build
cd build
cmake .. -G "Visual Studio 16 2019" -A x64
cmake --build . --config Release
cd ..
```
*Make sure `ir_converter.dll`, `AutelIrTempParserSDK.dll`, and `opencv_worldXXXX.dll` are in `build/Release/`.*

---
## 💻 Usage

### Command Line
Run the Python script to convert images.

```powershell
python thermal_converter.py <INPUT_PATH> <OUTPUT_FOLDER>
```

#### Examples
**Convert a single image:**
```powershell
python thermal_converter.py images/IRX_1234.JPG output/
```
*   Creates `output/IRX_1234.tif`
*   Creates `output/IRX_1234_meta.json`

**Convert a whole folder:**
```powershell
python thermal_converter.py images/ output_tifs/
```
*   Converts all JPGs in `images/` to `output_tifs/`
*   Creates `output_tifs/dataset_metadata.json` (aggregated metadata)

---
## 🌡️ Temperature Decoding (Band 4)

The thermal data (Band 4) is encoded as a **16-bit Unsigned Integer** to maximize compatibility with photogrammetry software (e.g., Metashape, ODMs) while preserving decimal precision and handling negative temperatures.

**Formula:**
$$ PixelValue = (Temperature°C \times 100) + 10000 $$

**How to Decode (in GIS/Python):**
$$ Temperature°C = \frac{PixelValue - 10000}{100.0} $$

**Examples:**
| Temp (°C) | Pixel Value (uint16) |
|:---:|:---:|
| -20.00 | 8000 |
| 0.00 | 10000 |
| 23.45 | 12345 |
| 100.00 | 20000 |

---
## 📄 API Documentation

For advanced integration (using the DLL directly in C# or C++), see [DLL_USAGE.md](DLL_USAGE.md).

---
## 📜 License
MIT License.
*Note: This project relies on the proprietary Autel Robotics IrTempParser SDK.*

