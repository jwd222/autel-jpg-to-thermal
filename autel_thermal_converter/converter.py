import ctypes
import os
import json
from pathlib import Path
import sys

def _get_dll_path():
    # Helper to find the DLL within the package
    base_path = os.path.dirname(os.path.abspath(__file__))
    dll_dir = os.path.join(base_path, 'libs')
    dll_path = os.path.join(dll_dir, 'ir_converter.dll')
    
    # On Windows, we need to add the directory to the DLL search path
    # so dependencies (Autel SDK, OpenCV) can be found.
    if os.name == 'nt':
        if hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(dll_dir)
            except OSError:
                pass 
        # Fallback/Additional measure: add to PATH
        os.environ['PATH'] = dll_dir + os.pathsep + os.environ.get('PATH', '')

    return dll_path

class ThermalConverter:
    def __init__(self):
        self.dll_path = _get_dll_path()
        if not os.path.exists(self.dll_path):
            raise FileNotFoundError(f"DLL not found at {self.dll_path}")
        
        try:
            # On Linux (or non-Windows), CDLL might behave differently, 
            # but these DLLs are Windows binaries.
            # If running via Wine or similar, this might work if configured correctly.
            self.lib = ctypes.CDLL(self.dll_path)
            self._setup_signatures()
        except OSError as e:
            raise OSError(f"Failed to load DLL: {e}. \nEnsure you are on Windows or have a compatible environment (Wine). \nDLL Path: {self.dll_path}") from e

    def _setup_signatures(self):
        self.lib.ConvertToTiff.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.ConvertToTiff.restype = ctypes.c_int
        
        self.lib.GetMetadataJSON.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
        self.lib.GetMetadataJSON.restype = ctypes.c_int

    def convert_image(self, input_path: str, output_path: str) -> bool:
        """Converts a single JPG to TIFF. Returns True on success."""
        if not os.path.exists(input_path):
            print(f"Error: File not found {input_path}")
            return False
            
        b_in = str(input_path).encode('utf-8')
        b_out = str(output_path).encode('utf-8')
        
        res = self.lib.ConvertToTiff(b_in, b_out)
        return res == 0

    def get_metadata(self, input_path: str) -> dict:
        """Extracts metadata from JPG. Returns dict or None."""
        if not os.path.exists(input_path):
            return None
            
        b_in = str(input_path).encode('utf-8')
        buffer_size = 1024 * 20 # 20KB
        buffer = ctypes.create_string_buffer(buffer_size)
        
        res = self.lib.GetMetadataJSON(b_in, buffer, buffer_size)
        if res == 0:
            try:
                return json.loads(buffer.value.decode('utf-8'))
            except json.JSONDecodeError:
                return None
        return None
