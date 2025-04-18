import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import date
import os
import pandas as pd
import re
import requests
import shutil
import threading
import webbrowser
from pathlib import Path


class BulkDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulk Downloader v4")
        self.root.geometry("800x600")

        # Variables
        self.df = None
        self.column_names = []
        self.csv_name = ""
        self.zip_name = ""
        self.selected_link_column = tk.StringVar()
        self.selected_file_name_columns = []
        self.download_progress = tk.StringVar(value="Ready")

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame, text="Bulk Downloader v4", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        # File uploader
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)

        file_label = ttk.Label(file_frame, text="Choose a CSV file:")
        file_label.pack(side=tk.LEFT, padx=5)

        self.file_path_var = tk.StringVar()
        file_path_entry = ttk.Entry(
            file_frame, textvariable=self.file_path_var, width=50
        )
        file_path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        browse_button = ttk.Button(file_frame, text="Browse", command=self.open_file)
        browse_button.pack(side=tk.LEFT, padx=5)

        # Link column selector
        link_frame = ttk.Frame(main_frame)
        link_frame.pack(fill=tk.X, pady=10)

        link_label = ttk.Label(link_frame, text="Which column has the download link?")
        link_label.pack(side=tk.LEFT, padx=5)

        self.link_column_combo = ttk.Combobox(
            link_frame, textvariable=self.selected_link_column, state="readonly"
        )
        self.link_column_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # File name columns selector
        filename_frame = ttk.Frame(main_frame)
        filename_frame.pack(fill=tk.BOTH, pady=10, expand=True)

        filename_label = ttk.Label(
            filename_frame, text="What information do you want in the file names?"
        )
        filename_label.pack(anchor=tk.W, padx=5, pady=5)

        # Create a frame for the checklist
        checklist_frame = ttk.Frame(filename_frame)
        checklist_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        # Scrollable area for checklist
        scroll_frame = ttk.Frame(checklist_frame)
        scroll_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.columns_listbox = tk.Listbox(
            scroll_frame, selectmode=tk.MULTIPLE, height=10
        )
        self.columns_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            scroll_frame, orient=tk.VERTICAL, command=self.columns_listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.columns_listbox.config(yscrollcommand=scrollbar.set)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)

        self.download_button = ttk.Button(
            button_frame, text="Run Downloader", command=self.run_downloader
        )
        self.download_button.pack(side=tk.LEFT, padx=5)

        self.download_zip_button = ttk.Button(
            button_frame,
            text="Open Download Folder",
            command=self.open_download_folder,
            state=tk.DISABLED,
        )
        self.download_zip_button.pack(side=tk.LEFT, padx=5)

        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=10)

        progress_label = ttk.Label(progress_frame, text="Status:")
        progress_label.pack(side=tk.LEFT, padx=5)

        self.progress_value = ttk.Label(
            progress_frame, textvariable=self.download_progress
        )
        self.progress_value.pack(side=tk.LEFT, padx=5)

        self.progress_bar = ttk.Progressbar(
            main_frame, orient=tk.HORIZONTAL, mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X, pady=10, padx=5)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.file_path_var.set(file_path)
            self.load_csv(file_path)

    def load_csv(self, file_path):
        try:
            self.df = pd.read_csv(file_path)
            self.column_names = list(self.df.columns)

            # Update link column dropdown
            self.link_column_combo["values"] = self.column_names
            if self.column_names:
                self.link_column_combo.current(0)

            # Update file name columns listbox
            self.columns_listbox.delete(0, tk.END)
            for col in self.column_names:
                self.columns_listbox.insert(tk.END, col)

            # Set csv_name
            self.csv_name = re.split(r"[/\\.]", file_path)[-2]

            # Enable download button
            self.download_button.config(state=tk.NORMAL)

            # Set zip name
            self.zip_name = f"{str(date.today())}_{self.csv_name}"

            messagebox.showinfo("Success", f"CSV loaded: {len(self.df)} rows")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {str(e)}")

    def check_unique(self, path, file_name_columns, row, url):
        """Ensure Unique File Names"""
        name = (
            "_".join([str(row[x]) for x in file_name_columns])
            + "."
            + url.split(".")[-1]
        )
        file_list = os.listdir(path)
        matches = [name == x for x in file_list]
        i = 1
        while matches.count(True) != 0:
            name = (
                "_".join([str(row[x]) for x in file_name_columns])
                + f"_{i}"
                + "."
                + url.split(".")[-1]
            )
            i = i + 1
            matches = [name == x for x in file_list]
        return name

    def save_image(self, path, file_name_columns, row, url):
        """Downloads images from the url to the path. file_name_columns specifies the name of the downloaded file."""
        # Make unique file name
        name = self.check_unique(path, file_name_columns, row, url)
        # Save file
        file_name = f"{path}/{name}"
        img_data = requests.get(url).content
        with open(f"{file_name}", "wb") as handler:
            handler.write(img_data)

    def bulk_download(self, df, link_column, file_name_columns, zip_name):
        """Run the downloader"""
        try:
            # Create download directory if it doesn't exist
            os.makedirs(zip_name, exist_ok=True)

            # Get URL Columns from selected options
            download_links = df[link_column].dropna()
            df_download = df.iloc[download_links.index]
            df_download = df_download.astype("str")

            total = len(df_download)

            # Download if url is present
            for idx in range(total):
                if idx % 5 == 0:  # Update progress every 5 items
                    progress = int((idx / total) * 100)
                    self.root.after(
                        0,
                        lambda p=progress: self.update_progress(
                            p, f"Downloading {idx+1}/{total}"
                        ),
                    )

                row = df_download.iloc[idx]
                self.save_image(zip_name, file_name_columns, row, row[link_column])

            # Zip files
            self.root.after(0, lambda: self.update_progress(95, "Creating ZIP file..."))
            shutil.make_archive(f"{zip_name}", "zip", zip_name)

            # Complete
            self.root.after(0, lambda: self.update_progress(100, "Download complete!"))
            self.root.after(0, lambda: self.download_zip_button.config(state=tk.NORMAL))

            return True
        except Exception as e:
            self.root.after(0, lambda: self.update_progress(0, f"Error: {str(e)}"))
            messagebox.showerror("Error", f"Download failed: {str(e)}")
            return False

    def update_progress(self, value, status):
        self.progress_bar["value"] = value
        self.download_progress.set(status)

    def run_downloader(self):
        if not self.df is not None:
            messagebox.showerror("Error", "Please load a CSV file first")
            return

        # Get selected link column
        link_column = self.selected_link_column.get()
        if not link_column:
            messagebox.showerror("Error", "Please select a column with download links")
            return

        # Get selected file name columns
        selected_indices = self.columns_listbox.curselection()
        if not selected_indices:
            messagebox.showerror(
                "Error", "Please select at least one column for file names"
            )
            return

        file_name_columns = [self.columns_listbox.get(i) for i in selected_indices]

        # Disable download button during processing
        self.download_button.config(state=tk.DISABLED)
        self.download_progress.set("Starting download...")
        self.progress_bar["value"] = 0

        # Run download in a separate thread to keep GUI responsive
        download_thread = threading.Thread(
            target=self.bulk_download,
            args=(self.df, link_column, file_name_columns, self.zip_name),
        )
        download_thread.daemon = True
        download_thread.start()

    def open_download_folder(self):
        """Open the folder containing the downloaded files"""
        zip_path = os.path.abspath(f"{self.zip_name}.zip")
        folder_path = os.path.dirname(zip_path)

        # Open folder with platform-specific command
        if os.path.exists(zip_path):
            webbrowser.open(f"file://{folder_path}")
        else:
            messagebox.showerror("Error", "Download folder not found")


if __name__ == "__main__":
    root = tk.Tk()
    app = BulkDownloaderApp(root)
    root.mainloop()
