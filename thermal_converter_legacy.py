import ctypes
import os
import json
import argparse
from pathlib import Path

# --- Configuration ---
DLL_PATH = r"build\Release\ir_converter.dll"
# ---------------------

def load_dll():
    """Loads the C++ DLL and configures function signatures."""
    if not os.path.exists(DLL_PATH):
        raise FileNotFoundError(f"Could not find DLL at: {DLL_PATH}")
    
    lib = ctypes.CDLL(DLL_PATH)
    
    # Configure ConvertToTiff
    # int ConvertToTiff(const char* inputPath, const char* outputPath)
    lib.ConvertToTiff.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.ConvertToTiff.restype = ctypes.c_int
    
    # Configure GetMetadataJSON
    # int GetMetadataJSON(const char* inputPath, char* buffer, int bufferLen)
    lib.GetMetadataJSON.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    lib.GetMetadataJSON.restype = ctypes.c_int
    
    return lib

def process_single_file(lib, input_path, output_dir):
    """Processes a single JPG file."""
    p_in = Path(input_path)
    if not p_in.exists():
        print(f"Error: File not found {input_path}")
        return None

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct output paths
    stem = p_in.stem
    p_out_tif = os.path.join(output_dir, f"{stem}.tif")
    
    # Convert Image
    # Encode paths for C++
    b_in = str(p_in).encode('utf-8')
    b_out = str(p_out_tif).encode('utf-8')
    
    res = lib.ConvertToTiff(b_in, b_out)
    if res != 0:
        print(f"❌ Failed to convert {p_in.name} (Error code: {res})")
        return None
        
    print(f"✅ Converted: {p_in.name} -> {os.path.basename(p_out_tif)}")
    
    # Extract Metadata
    buffer_size = 1024 * 10 # 10KB buffer should be plenty
    buffer = ctypes.create_string_buffer(buffer_size)
    
    res_meta = lib.GetMetadataJSON(b_in, buffer, buffer_size)
    if res_meta == 0:
        json_str = buffer.value.decode('utf-8')
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            print(f"⚠️ Failed to decode JSON for {p_in.name}")
            return None
    else:
        print(f"⚠️ Failed to get metadata for {p_in.name}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Autel Thermal JPG to TIFF Converter")
    parser.add_argument("input", help="Path to a single JPG file or a directory of JPGs")
    parser.add_argument("output", help="Directory to save output TIFFs and JSON")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_dir = args.output
    
    lib = load_dll()
    
    full_metadata = {}
    
    if input_path.is_file():
        # Single File Mode
        print(f"🔍 Processing single file: {input_path}")
        meta = process_single_file(lib, input_path, output_dir)
        if meta:
            # Save single JSON
            json_name = f"{input_path.stem}_meta.json"
            with open(os.path.join(output_dir, json_name), 'w') as f:
                json.dump(meta, f, indent=4)
            print(f"📄 Saved metadata: {json_name}")
            
    elif input_path.is_dir():
        # Directory Mode
        print(f"📂 Processing folder: {input_path}")
        count = 0
        success = 0
        
        for file in input_path.glob("*.[jJ][pP][gG]"): # Match .jpg .JPG etc
            count += 1
            meta = process_single_file(lib, file, output_dir)
            if meta:
                success += 1
                full_metadata[file.name] = meta
        
        # Save aggregated JSON
        if full_metadata:
            json_path = os.path.join(output_dir, "dataset_metadata.json")
            with open(json_path, 'w') as f:
                json.dump(full_metadata, f, indent=4)
            print(f"\n📚 Saved aggregated metadata to: {json_path}")
            
        print(f"\n🎉 Finished. Processed {count} images, {success} successful.")
        
    else:
        print("❌ Invalid input path.")

if __name__ == "__main__":
    main()
