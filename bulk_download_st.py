from datetime import date

import getpass
import os
import pandas as pd
import re
import requests
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


def bulk_download(df, link_column, uploaded_file, file_name_columns, path):
    """Run the downloader"""
    # Localize variables
    file_name_columns = file_name_columns
    path = path
    link_column = link_column
    df = df.copy()
    df = df.astype("str")

    # Make output folder
    try:
        os.mkdir(path)
    except:
        pass

    # Get URL Columns from Widgets
    download_links = df[link_column].dropna()
    df_download = df.iloc[download_links.index]

    # Download if url is present
    for idx in range(len(df_download)):
        row = df_download.iloc[idx]
        save_image(path, file_name_columns, row, row[link_column])


# Title
st.write("Bulk Downloader v4")

# Open CSV
uploaded_file = st.file_uploader(label="Choose a file:", type=["csv"])
column_names = []  # Avoid streamlit exception
csv_name = ""  # Avoid streamlit exception
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    column_names = list(df.columns)
    csv_name = re.split("[\.]", uploaded_file.name)[0]

# Select URL Column
link_column = st.selectbox("Which column has the download link?", column_names)

# Output name and location
folder_name = st.text_input(
    label="Output Folder Name:", value=f"{str(date.today())}-{csv_name}"
)
user_name = getpass.getuser()
path = f"/Users/{user_name}/Downloads/{folder_name}"

# Select File Name Columns
file_name_columns = st.multiselect(
    "What information you want in the file names?", column_names
)

# Run Downloader Button
if st.button("Run Downloader"):
    bulk_download(df, link_column, csv_name, file_name_columns, path)
