import sys
import os
import re
import threading
import pandas as pd
import requests
import shutil
from datetime import date
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QComboBox,
    QListWidget,
    QProgressBar,
    QListWidgetItem,
    QMessageBox,
    QLineEdit,
)
from PySide6.QtCore import Qt, Signal, QObject, QUrl
from PySide6.QtGui import QDesktopServices


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""

    progress = Signal(int, str)
    finished = Signal(bool, str)


class BulkDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bulk Downloader v5")
        self.setMinimumSize(800, 600)

        # App state variables
        self.df = None
        self.column_names = []
        self.csv_name = ""
        self.zip_name = ""
        self.worker_signals = WorkerSignals()

        # Setup UI
        self.setup_ui()

        # Connect signals
        self.worker_signals.progress.connect(self.update_progress)
        self.worker_signals.finished.connect(self.download_finished)

    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("Bulk Downloader v5")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # File selection section
        file_layout = QHBoxLayout()
        file_label = QLabel("Choose a CSV file:")
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.open_file)

        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_path_input, 1)
        file_layout.addWidget(browse_button)
        main_layout.addLayout(file_layout)

        # Link column selection
        link_layout = QHBoxLayout()
        link_label = QLabel("Which column has the download link?")
        self.link_column_combo = QComboBox()

        link_layout.addWidget(link_label)
        link_layout.addWidget(self.link_column_combo, 1)
        main_layout.addLayout(link_layout)

        # File name columns selection
        main_layout.addWidget(QLabel("What information do you want in the file names?"))

        self.columns_list = QListWidget()
        self.columns_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        main_layout.addWidget(self.columns_list, 1)

        # Action buttons
        buttons_layout = QHBoxLayout()
        self.download_button = QPushButton("Run Downloader")
        self.download_button.clicked.connect(self.run_downloader)
        self.download_button.setEnabled(False)

        self.open_folder_button = QPushButton("Open Download Folder")
        self.open_folder_button.clicked.connect(self.open_download_folder)
        self.open_folder_button.setEnabled(False)

        buttons_layout.addWidget(self.download_button)
        buttons_layout.addWidget(self.open_folder_button)
        main_layout.addLayout(buttons_layout)

        # Progress section
        progress_layout = QHBoxLayout()
        progress_label = QLabel("Status:")
        self.progress_status = QLabel("Ready")

        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_status, 1)
        main_layout.addLayout(progress_layout)

        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv)"
        )
        if file_path:
            self.file_path_input.setText(file_path)
            self.load_csv(file_path)

    def load_csv(self, file_path):
        try:
            self.df = pd.read_csv(file_path)
            self.column_names = list(self.df.columns)

            # Update link column dropdown
            self.link_column_combo.clear()
            self.link_column_combo.addItems(self.column_names)

            # Update file name columns list
            self.columns_list.clear()
            for col in self.column_names:
                item = QListWidgetItem(col)
                self.columns_list.addItem(item)

            # Set csv_name from file path
            file_name = os.path.basename(file_path)
            self.csv_name = os.path.splitext(file_name)[0]

            # Set zip name/directory name for downloaded pictures
            self.zip_name = f"{str(date.today())}_{self.csv_name}"

            # Enable download button
            self.download_button.setEnabled(True)

            QMessageBox.information(self, "Success", f"CSV loaded: {len(self.df)} rows")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSV file: {str(e)}")

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

    def bulk_download_thread(self, df, link_column, file_name_columns, zip_name):
        """Run the downloader in a separate thread"""
        try:
            # Create download directory for pics in ~/Downloads if it doesn't exist
            downloads_path = os.path.join(Path.home(), "Downloads")
            dir_name = os.path.join(downloads_path, zip_name)
            os.makedirs(dir_name, exist_ok=True)

            # Get URL Columns from selected options
            download_links = df[link_column].dropna()
            df_download = df.iloc[download_links.index]
            df_download = df_download.astype("str")

            total = len(df_download)

            # Download if url is present
            for idx in range(total):
                if idx % 5 == 0 or idx == total - 1:  # Update progress every 5 items
                    progress = int((idx / total) * 100)
                    self.worker_signals.progress.emit(
                        progress, f"Downloading {idx+1}/{total}"
                    )

                row = df_download.iloc[idx]
                self.save_image(dir_name, file_name_columns, row, row[link_column])

            # Zip files
            # self.worker_signals.progress.emit(95, "Creating ZIP file...")
            # shutil.make_archive(f"{zip_name}", "zip", zip_name)

            # Signal completion
            self.worker_signals.finished.emit(True, "Download complete!")

        except Exception as e:
            self.worker_signals.finished.emit(False, f"Error: {str(e)}")

    def update_progress(self, value, status):
        self.progress_bar.setValue(value)
        self.progress_status.setText(status)

    def download_finished(self, success, message):
        self.update_progress(100 if success else 0, message)
        self.download_button.setEnabled(True)
        self.open_folder_button.setEnabled(success)

        if not success:
            QMessageBox.critical(self, "Error", message)

    def run_downloader(self):
        if self.df is None:
            QMessageBox.warning(self, "Warning", "Please load a CSV file first")
            return

        # Get selected link column
        link_column = self.link_column_combo.currentText()
        if not link_column:
            QMessageBox.warning(
                self, "Warning", "Please select a column with download links"
            )
            return

        # Get selected file name columns
        selected_items = self.columns_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Warning", "Please select at least one column for file names"
            )
            return

        file_name_columns = [item.text() for item in selected_items]

        # Disable download button during processing
        self.download_button.setEnabled(False)
        self.progress_status.setText("Starting download...")
        self.progress_bar.setValue(0)

        # Run download in a separate thread to keep GUI responsive
        download_thread = threading.Thread(
            target=self.bulk_download_thread,
            args=(self.df, link_column, file_name_columns, self.zip_name),
        )
        download_thread.daemon = True
        download_thread.start()

    def open_download_folder(self):
        """Open the folder containing the downloaded files"""
        zip_path = os.path.abspath(f"{self.zip_name}.zip")
        folder_path = os.path.dirname(zip_path)

        if os.path.exists(zip_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
        else:
            QMessageBox.critical(self, "Error", "Download folder not found")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style to match native macOS look
    app.setStyle("Fusion")

    window = BulkDownloaderApp()
    window.show()

    sys.exit(app.exec())
