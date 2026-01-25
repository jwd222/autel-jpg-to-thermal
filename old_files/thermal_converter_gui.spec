# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['thermal_converter_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('build/Release/batch_ir2tif.exe', 'build/Release'),  # Include C++ executable
        # Add OpenCV DLLs if needed (uncomment and adjust paths):
        # ('C:/opencv/build/x64/vc16/bin/opencv_world4XX.dll', 'build/Release'),
        # ('path/to/your/Autel_SDK.dll', 'build/Release'),  # If you have SDK DLLs
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ThermalConverter',  # Better name without _gui suffix
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see debug output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Add this line if you have an icon file
)