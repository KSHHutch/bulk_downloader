# bulk_downloader

The bulk_downloader app is an extremely simple Streamlit app to automate downloading images or pdfs from a list of URLs. It's pretty basic in its scope and implemenatation.

It expects a CSV file input. You select which column contains the URLs, and which columns you want the downloaded file names.

It downloads files to the app, then zips it up. After that process is finished a button will appear with the option to download as .zip to your computer locally.

## Update Apr. 2025

Streamlit version was being finicky, created versions meant to be run locally. GUIs constructed using tkinter and pyside (mostly as a learning project for me). PySide6 app is much more performant and better looking to boot, tkinter does have the advantage of fewer to no dependencies.

`setup.py` file is for packaging using `py2app`.
Can create a proper MacOS app bundle by running

```bash
python setup.py py2app
```

so long as `setup.py` points to `bulk_download_pyside.py`.
