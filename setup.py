from setuptools import setup

APP = ["bulk_download_pyside.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": True,
    "packages": ["PySide6", "pandas", "requests"],
    "iconfile": "downloader.icns",
    "excludes": ["psycopg2"],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
