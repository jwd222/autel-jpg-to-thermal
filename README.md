# Autel Thermal Image Converter

Convert Autel thermal JPEG images to scientific-grade temperature TIFF files using the official **IrTempParse SDK**.

This tool extracts per-pixel temperature data from Autel IR photos (e.g., from EVO II Dual, Dragonfish) and saves it as a single-band 32-bit float GeoTIFF-compatible file for use in GIS, scientific analysis, or custom processing.

---

## 📦 Features

- ✅ Batch process entire folders of Autel `.jpg` thermal images  
- ✅ Outputs per-pixel temperature values (°C) as `.tif` files  
- ✅ Preserves original filenames (e.g., `IRX_1234.JPG` → `IRX_1234.tif`)  
- ✅ Includes a user-friendly GUI (Windows `.exe` included)  
- ✅ Built on Autel’s official **IrTempParse SDK v2.5**

---

## 🛠️ Requirements

- **Input**: Thermal images from **Autel cameras** (e.g., `.jpg` files with embedded IR data)
- **OS**: Windows 10/11 (64-bit)
- **Resolution**: Images must be **640×512 pixels** (standard for many Autel models)

> ❗ Regular JPEGs or thermal images from FLIR/DJI **will not work**.

---

## 🚀 Quick Start (GUI)

1. **Download** the latest release (`AutelThermalConverter.zip`)
2. **Extract** the folder
3. **Run** `thermal_converter_gui.exe`
4. Select:
   - **Input folder**: containing Autel `.jpg` files
   - **Output folder**: where `.tif` files will be saved
5. Click **"Convert Images"**

✅ Done! Your temperature TIFFs are ready for analysis in QGIS, Python, ENVI, etc.

---

## 🧑‍💻 CLI Usage (Advanced)

The core converter is a command-line tool:

```powershell
batch_ir2tif.exe "C:/input_folder" "C:/output_folder"
```

Output:
- One `.tif` per `.jpg`
- 32-bit float, single band
- Pixel values = temperature in **°C**

---

## 📂 Folder Structure (Source Build)

```
autel_thermal_converter/
├── thermal_converter_gui.exe      ← Standalone GUI app
├── build/Release/
│   ├── batch_ir2tif.exe           ← CLI converter
│   ├── AutelIrTempParserSDK.dll   ← Required SDK
│   └── opencv_world4120.dll       ← OpenCV runtime
├── README.md
└── LICENSE
```

---

## 🔧 Building from Source

### Prerequisites
- Visual Studio 2022 (or Build Tools)
- CMake 3.20+
- OpenCV 4.12.0 (prebuilt, world version)

### Steps
```powershell
git clone <this-repo>
cd autel_thermal_converter
mkdir build && cd build
cmake .. -G "Visual Studio 17 2022" -A x64 -DOpenCV_DIR="C:/opencv/build"
cmake --build . --config Release
```

Then package the GUI:
```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "build/Release;build/Release" thermal_converter_gui.py
```

---

## 📄 Output Format

- **File**: `.tif` (TIFF)
- **Data type**: 32-bit floating point (`float32`)
- **Band**: 1 (temperature in °C)
- **Dimensions**: 640 × 512
- **No georeferencing** (pure raster)

> 🔍 Open in Python:
> ```python
> import rasterio
> with rasterio.open('image.tif') as src:
>     temps = src.read(1)  # numpy array of °C values
> ```

---

## ⚠️ Notes

- The SDK only supports **Autel-branded thermal images** with embedded metadata.
- Do not rename or edit the `.dll` files — they are required at runtime.
- Antivirus may flag the `.exe` (false positive due to PyInstaller). Add an exception if needed.

---

## 📜 License

- This wrapper is open source (MIT License)
- The **IrTempParse SDK** is proprietary to **Autel Robotics** — use in compliance with their terms.

---

## 🙏 Acknowledgements

- [Autel Robotics](https://www.autelrobotics.com/) – for the IrTempParse SDK
- [OpenCV](https://opencv.org/) – for image I/O
- [PyInstaller](https://www.pyinstaller.org/) – for packaging

---

> 🌡️ Turn your drone’s thermal vision into actionable scientific data — one pixel at a time.