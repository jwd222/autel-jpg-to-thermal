import argparse
import os
import json
from pathlib import Path
from .converter import ThermalConverter

def main():
    parser = argparse.ArgumentParser(description="Autel Thermal JPG to TIFF Converter")
    parser.add_argument("input", help="Path to a single JPG file or a directory of JPGs")
    parser.add_argument("output", help="Directory to save output TIFFs and JSON")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_dir = Path(args.output)
    
    try:
        converter = ThermalConverter()
    except Exception as e:
        print(f"Failed to initialize converter: {e}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    full_metadata = {}
    
    if input_path.is_file():
        # Single File Mode
        print(f"🔍 Processing single file: {input_path}")
        # Construct output path
        output_file = output_dir / f"{input_path.stem}.tif"
        
        success = converter.convert_image(str(input_path), str(output_file))
        if success:
            print(f"✅ Converted: {output_file.name}")
            meta = converter.get_metadata(str(input_path))
            if meta:
                json_name = f"{input_path.stem}_meta.json"
                with open(output_dir / json_name, 'w') as f:
                    json.dump(meta, f, indent=4)
                print(f"📄 Saved metadata: {json_name}")
        else:
            print(f"❌ Failed to convert {input_path.name}")
            
    elif input_path.is_dir():
        # Directory Mode
        print(f"📂 Processing folder: {input_path}")
        count = 0
        success_count = 0
        
        # Match case-insensitive .jpg
        files = []
        for ext in ['*.jpg', '*.JPG', '*.jpeg', '*.JPEG']:
            files.extend(input_path.glob(ext))
        files = sorted(list(set(files))) # Unique files
        
        for file in files:
            count += 1
            output_file = output_dir / f"{file.stem}.tif"
            
            if converter.convert_image(str(file), str(output_file)):
                success_count += 1
                print(f"✅ {file.name}")
                meta = converter.get_metadata(str(file))
                if meta:
                    full_metadata[file.name] = meta
            else:
                print(f"❌ {file.name}")
        
        # Save aggregated JSON
        if full_metadata:
            json_path = output_dir / "dataset_metadata.json"
            with open(json_path, 'w') as f:
                json.dump(full_metadata, f, indent=4)
            print(f"\n📚 Saved aggregated metadata to: {json_path}")
            
        print(f"\n🎉 Finished. Processed {count} images, {success_count} successful.")
        
    else:
        print("❌ Invalid input path.")

if __name__ == "__main__":
    main()
