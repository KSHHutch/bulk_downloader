import streamlit as st
import pandas as pd
from datetime import date
import os
import csv
import getpass
import requests
import re
import numpy as np


# Functions
def save_image(path, file_name_columns, row, url):
    """Downloads images from the url to the path.  file_name_columns specifies the name of the downloaded file."""
    # Make unique file name
    name = check_unique(path, file_name_columns, row, url)

    # Save file
    file_name = f"{path}/{name}"
    img_data = requests.get(url).content
    with open(f"{file_name}", "wb") as handler:
        handler.write(img_data)


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


def bulk_download(link_column, csv_name, file_name_columns, path):
    # Make output folder
    try:
        os.mkdir(path)
    except:
        pass

    # Get URL Columns from Widgets
    link_column = link_column
    csv_name = csv_name

    # Download if url is present
    with open(csv_name, newline="") as csvfile:
        read_csv = csv.DictReader(csvfile, delimiter=",")
        for row in read_csv:
            if row[link_column] == "" or row[link_column] == np.nan:
                pass
            else:
                save_image(path, file_name_columns, row, row[link_column])


st.write("Bulk Downloader v4")

# Open CSV
uploaded_file = st.file_uploader(label="Choose a file:", type=["csv"])
column_names = []
csv_name = ""

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    column_names = list(df.columns)
    csv_name = re.split("[\.]", uploaded_file.name)[0]

st.write(f"{csv_name}")

# Select URL Column
link_column = st.selectbox("Which column has the download link?", column_names)

# Output name and location
today = str(date.today())
folder_name = st.text_input(label="Output Folder Name:", value=f"{today}-{csv_name}")
user_name = getpass.getuser()
path = f"/Users/{user_name}/Downloads/{folder_name}"

# Select File Name Columns
file_name_columns = st.multiselect(
    "What information you want in the downloaded file names?", column_names
)

# Run Downloader Button
if st.button("Run Downloader"):
    bulk_download(link_column, csv_name, file_name_columns, path)


## TODO
# Rejigger downloader so it draws on the dataframe made from the CSV to download instead of the raw CSV
