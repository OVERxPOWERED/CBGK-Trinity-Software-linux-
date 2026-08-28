from setuptools import setup, find_packages

setup(
    name="cbgk",
    version="1.0.0",
    description="Linux Driver and Material 3 Control Center for Cosmic Byte Trinity Gaming Keyboard",
    author="OVERxPOWERED",
    packages=find_packages(),
    scripts=["bin/cbgk", "bin/cbgk-gui"],
    install_requires=[
        "PyQt6>=6.4.0",
        "Pillow>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cbgk=bin.cbgk:main",
            "cbgk-gui=bin.cbgk_gui:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
)
