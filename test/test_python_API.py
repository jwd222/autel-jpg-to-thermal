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
