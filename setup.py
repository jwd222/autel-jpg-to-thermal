from setuptools import setup, find_packages

setup(
    name="autel_thermal_converter",
    version="0.1.0",
    description="Python package to convert Autel thermal JPGs to TIFF using Autel SDK",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "autel_thermal_converter": ["libs/*.dll"],
    },
    entry_points={
        "console_scripts": [
            "autel-convert=autel_thermal_converter.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
)
