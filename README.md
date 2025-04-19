# bulk_downloader

The bulk_downloader app is an extremely simple Streamlit app to automate downloading images or pdfs from a list of URLs. It's pretty basic in its scope and implemenatation.

It expects a CSV file input. You select which column contains the URLs, and which columns you want the downloaded file names.

It downloads files to the app, then zips it up. After that process is finished a button will appear with the option to download as .zip to your computer locally.

## Update Apr. 2025

Streamlit version was being finicky, created versions meant to be run locally. GUIs constructed using tkinter and pyside (mostly as a learning project for me). PySide6 app is much more performant and better looking to boot, tkinter does have the advantage of fewer to no dependencies.

Tried py2app and pyinstaller for distribution. py2app unfortunately didn't work, so I went with pyinstaller instead. Keeping the `setup.py` file around for reference.

Bundled for using locally by running:

```bash
pip install pyinstaller
pyinstaller --name "BulkDownloader" \
            --windowed \
            --icon=downloader.icns \
            --hidden-import PySide6 \
            bulk_download_pyside.py
```
