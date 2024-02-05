import streamlit as st
import pandas as pd
from datetime import date
import os
import getpass

st.write("Bulk Downloader v4")

# Open CSV
uploaded_file = st.file_uploader(label="Choose a file:", type=["csv"])
path = ""
column_names = []

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    column_names = list(df.columns)

st.write(f"{path}")


# Select URL Column
link_column = st.selectbox("Which column has the URL?", column_names)

# Output name and location
today = str(date.today())
folder_name = st.text_input(
    label="Output Folder Name:", value=f"{today}-{uploaded_file.file.name}"
)


# Select File Name Columns


# Ensure unique file names
def check_unique(path, file_name_widget, row, url):
    """Ensure Unique File Names"""
    name = "_".join([row[x] for x in file_name_widget.value]) + "." + url.split(".")[-1]
    file_list = os.listdir(path)
    matches = [name == x for x in file_list]
    i = 1
    while matches.count(True) != 0:
        name = (
            "_".join([row[x] for x in file_name_widget.value])
            + f"_{i}"
            + "."
            + url.split(".")[-1]
        )
        i = i + 1
        matches = [name == x for x in file_list]
    return name


def make_output_folder(folder_name=str(date.today())):
    try:
        # Make new folder
        user_name = getpass.getuser()
        name = folder_name
        path = f"Users/{user_name}/Downloads/{name}"
        os.mkdir(path)
    except:
        pass


def bulk_download(link_column, uploaded_file):
    # Get URL Columns from Widgets
    url_column = link_column
    csv_name = uploaded_file.name

    # Download if url is present
    with open(csv_name, newline="") as csvfile:
        read_csv = csv.DictReader(csvfile, delimiter=",")
        for row in read_csv:
            if row[url_column] == "":
                pass
            else:
                save_image(path, file_name_box, row, row[url_column])
