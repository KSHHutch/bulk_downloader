from datetime import date

import getpass
import os
import pandas as pd
import re
import requests
import shutil
import streamlit as st


# Functions
def check_unique(path, file_name_columns, row, url):
    """Ensure Unique File Names"""
    name = "_".join([row[x] for x in file_name_columns]) + "." + url.split(".")[-1]
    file_list = os.listdir(path)
    matches = [name == x for x in file_list]
    i = 1
    while matches.count(True) != 0:
        name = (
            "_".join([row[x] for x in file_name_columns])
            + f"_{i}"
            + "."
            + url.split(".")[-1]
        )
        i = i + 1
        matches = [name == x for x in file_list]
    return name


def save_image(path, file_name_columns, row, url):
    """Downloads images from the url to the path.  file_name_columns specifies the name of the downloaded file."""
    # Make unique file name
    name = check_unique(path, file_name_columns, row, url)

    # Save file
    file_name = f"{path}/{name}"
    img_data = requests.get(url).content
    with open(f"{file_name}", "wb") as handler:
        handler.write(img_data)


def bulk_download(df, link_column, uploaded_file, file_name_columns, zip_name):
    """Run the downloader"""
    # Localize variables
    file_name_columns = file_name_columns
    link_column = link_column
    df = df.copy()

    # Get URL Columns from Widgets
    download_links = df[link_column].dropna()
    df_download = df.iloc[download_links.index]
    df_download = df_download.astype("str")

    # Download if url is present
    for idx in range(len(df_download)):
        row = df_download.iloc[idx]
        save_image(zip_name, file_name_columns, row, row[link_column])

    # Zip files
    shutil.make_archive(f"{zip_name}", "zip", zip_name)


# Title
st.write("Bulk Downloader v4")

# Open CSV
uploaded_file = st.file_uploader(label="Choose a file:", type=["csv"])
column_names = []  # Avoid streamlit exception
csv_name = ""  # Avoid streamlit exception
zip_name = ""
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    column_names = list(df.columns)
    csv_name = re.split("[\.]", uploaded_file.name)[0]

    # Output folder and zip
    zip_name = f"{str(date.today())}_{csv_name}"
    try:
        os.mkdir(zip_name)
    except:
        pass


# Select URL Column
link_column = st.selectbox("Which column has the download link?", column_names)


# Select File Name Columns
file_name_columns = st.multiselect(
    "What information you want in the file names?", column_names
)

# Run Downloader Button
if st.button("Run Downloader"):
    bulk_download(df, link_column, csv_name, file_name_columns, zip_name)
    with open(f"{zip_name}.zip", "rb") as fp:
        btn = st.download_button(
            label="Download files as .zip",
            data=fp,
            file_name=f"{zip_name}.zip",
            mime="application/zip",
        )


def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


# TODO
## Figure out a way to use Streamlit's
