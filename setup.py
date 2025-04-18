from setuptools import setup

APP = ["bulk_downloader_pyside.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": True,
    "packages": ["PySide6", "pandas", "requests"],
    "iconfile": "downloader.icns",
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
