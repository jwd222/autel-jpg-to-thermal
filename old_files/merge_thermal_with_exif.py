import os
import subprocess
import rasterio
from pathlib import Path
import argparse
import sys

# add exiftool path "C:/exiftool/exiftool.exe" to system PATH if needed
if os.name == 'nt':
    exiftool_path = Path("C:/exiftool")
    os.environ["PATH"] += os.pathsep + str(exiftool_path)

def run_exiftool(src_jpg: Path, dst_tif_with_exif: Path):
    """Create a 16-bit TIFF from JPG with full EXIF/GPS using ExifTool"""
    cmd = [
        "exiftool",
        "-tagsFromFile", str(src_jpg),
        "-int16",  # creates 16-bit TIFF
        "-overwrite_original",
        str(dst_tif_with_exif)
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"ExifTool failed: {result.stderr.decode()}")
    # ExifTool creates file.tif_original → remove it
    backup = dst_tif_with_exif.with_name(dst_tif_with_exif.stem + ".tif_original")
    if backup.exists():
        backup.unlink()

def merge_thermal_and_exif(jpg_dir: Path, thermal_tif_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    for jpg in sorted(jpg_dir.glob("*.JPG")):
        thermal_tif = thermal_tif_dir / f"{jpg.stem}.tif"
        if not thermal_tif.exists():
            print(f"⚠️ Thermal TIFF missing for {jpg.name}, skipping")
            continue

        final_tif = output_dir / f"{jpg.stem}.tif"

        # Step 1: Create EXIF-enabled TIFF from JPG
        print(f"📸 Creating EXIF template for {jpg.name}")
        run_exiftool(jpg, final_tif)

        # Step 2: Read thermal data
        with rasterio.open(thermal_tif) as src:
            thermal_data = src.read(1)
            profile = src.profile.copy()

        # Step 3: Overwrite pixel data in EXIF-enabled TIFF
        with rasterio.open(final_tif, 'r+') as dst:
            dst.write(thermal_data, 1)
            # Preserve dtype and dimensions
            assert dst.shape == thermal_data.shape, "Shape mismatch!"

        print(f"✅ Merged: {final_tif.name}")

def main():
    parser = argparse.ArgumentParser(description="Merge thermal TIFFs with EXIF from JPGs")
    parser.add_argument("jpg_dir", type=Path, help="Directory with original JPGs")
    parser.add_argument("thermal_tif_dir", type=Path, help="Directory with thermal TIFFs (from C++)")
    parser.add_argument("output_dir", type=Path, help="Output directory for final TIFFs")

    args = parser.parse_args()

    merge_thermal_and_exif(args.jpg_dir, args.thermal_tif_dir, args.output_dir)
    print("\n🎉 All done! Final TIFFs have thermal data + full EXIF/GPS.")

if __name__ == "__main__":
    main()