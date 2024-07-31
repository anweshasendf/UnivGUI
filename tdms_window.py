from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtCore import Qt
import logging
import os
from nptdms import TdmsFile
import pandas as pd
import shutil 
from script_window import *
from PyQt5.QtCore import pyqtSignal
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtCore import Qt
import sqlite3
import logging
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
import os 
from PyQt5.QtWidgets import QHBoxLayout


logger = logging.getLogger(__name__)

class TDMSTypeWindow(QMainWindow):
    
    upload_completed = pyqtSignal(str, str)
    
    def __init__(self, previous_window=None, selected_option=None ):
        super().__init__()
        self.previous_window = previous_window
        self.selected_option = selected_option
        self.upload_window = None
        self.setWindowTitle("Choose TDMS Type")
        self.setGeometry(100, 100, 1050, 750)
        self.tdms_file_count = 0
        logger.info("TDMS Type selection window opened")
        self.showMaximized()
        self.set_background_image(r"Danfoss_BG.png")


        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.button_single = QPushButton("Single TDMS Folder")
        self.button_single.clicked.connect(self.open_single_upload)
        self.layout.addWidget(self.button_single)

        self.button_coupled = QPushButton("Coupled TDMS Folder")
        self.button_coupled.clicked.connect(self.open_coupled_upload)
        self.layout.addWidget(self.button_coupled)

        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        self.layout.addWidget(self.button_previous)
        
        self.set_logo()

    def open_single_upload(self):
        logger.info("Single TDMS folder selected")
        self.upload_window = UploadWindow(previous_window=self, selected_option=self.selected_option)
        self.upload_window.upload_completed.connect(self.on_upload_completed)
        self.upload_window.show()
        self.close()

    def open_coupled_upload(self):
        logger.info("Coupled TDMS folder selected")
        self.coupled_upload_window = CoupledUploadWindow(previous_window=self, selected_option=self.selected_option)
        self.coupled_upload_window.upload_completed.connect(self.on_upload_completed)
        self.coupled_upload_window.show()
        self.close()
        
    def update_tdms_file_count(self, folder_path):
        self.tdms_file_count = sum(1 for file in os.listdir(folder_path) if file.endswith('.tdms'))

    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)
    
    def set_logo(self):
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "Danfoss_Logo.png")
            if not os.path.exists(logo_path):
                print(f"Logo file not found at {logo_path}")
                return

            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            if pixmap.isNull():
                print("Failed to load the logo image")
                return

            scaled_pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setStyleSheet("background-color: transparent;")
            logo_label.setFixedSize(200, 100) 
            
            
            logo_container = QWidget()
            logo_container.setFixedSize(self.width(), 120)  
            logo_layout = QHBoxLayout(logo_container)
            logo_layout.addWidget(logo_label, alignment=Qt.AlignTop | Qt.AlignLeft)
            logo_layout.setContentsMargins(20, 20, 0, 0)  # Add some margin to position the logo
            
            # Insert the logo container at the top of the main layout
            self.layout.insertWidget(0, logo_container)
            
            print(f"Logo set successfully from {logo_path}")
            print(f"Logo size: {logo_label.size()}")
        except Exception as e:
            print(f"Error setting logo: {str(e)}")

    
    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()
            
    def on_upload_completed(self, folder_path):
        self.upload_completed.emit(folder_path, self.selected_option)
        
    def select_option(self, option):
        self.option_selected.emit(option)
        self.close()




class UploadWindow(QMainWindow):
    upload_completed = pyqtSignal(str)
    
    def __init__(self, previous_window=None, selected_option=None):
        super().__init__()
        self.previous_window = previous_window
        self.selected_option = selected_option
        self.setWindowTitle("Upload Folder")
        self.setGeometry(100, 100, 1050, 750)
        logger.info("Upload window opened")
        self.showMaximized()
        # Set background image
        self.set_background_image(r"Danfoss_BG.png")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.button_upload_folder = QPushButton("Upload TDMS Folder")
        self.button_upload_folder.clicked.connect(self.read_tdms_folder)
        self.layout.addWidget(self.button_upload_folder)

        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        self.layout.addWidget(self.button_previous)
        self.set_logo()
        
    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)
    
    def set_logo(self):
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "Danfoss_Logo.png")
            if not os.path.exists(logo_path):
                print(f"Logo file not found at {logo_path}")
                return

            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            if pixmap.isNull():
                print("Failed to load the logo image")
                return

            scaled_pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setStyleSheet("background-color: transparent;")
            logo_label.setFixedSize(200, 100) 
            
            
            logo_container = QWidget()
            logo_container.setFixedSize(self.width(), 120)  
            logo_layout = QHBoxLayout(logo_container)
            logo_layout.addWidget(logo_label, alignment=Qt.AlignTop | Qt.AlignLeft)
            logo_layout.setContentsMargins(20, 20, 0, 0)  # Add some margin to position the logo
            
            # Insert the logo container at the top of the main layout
            self.layout.insertWidget(0, logo_container)
            
            print(f"Logo set successfully from {logo_path}")
            print(f"Logo size: {logo_label.size()}")
        except Exception as e:
            print(f"Error setting logo: {str(e)}")


    def read_tdms_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select TDMS Folder")
        if folder_path:
            logger.info(f"Folder uploaded: {folder_path}")
            data = {}
            seen_files = set()
            for root, _, files in os.walk(folder_path):
                for file_name in files:
                    if file_name.endswith('.tdms'):
                        if file_name in seen_files:
                            logger.warning(f"Duplicate file ignored: {file_name}")
                            continue
                        seen_files.add(file_name)
                        file_path = os.path.join(root, file_name)
                        tdms_file = TdmsFile.read(file_path)
                        for group in tdms_file.groups():
                            if group.name == 'piston_group':
                                df = group.as_dataframe()
                                if group.name not in data:
                                    data[group.name] = df
                                else:
                                    try:
                                        data[group.name] = pd.concat([data[group.name], df]).drop_duplicates().reset_index(drop=True)
                                    except Exception as e:
                                        logger.error(f"Error concatenating data for file {file_name}: {e}")
            self.previous_window.update_tdms_file_count(folder_path)
            self.upload_completed.emit(folder_path)
            self.close()
            script_path = r"pcr_rr_new.py" if self.selected_option == "PC RR" else r"piston_group.py"

            self.script_upload_window = ScriptUploadWindow(folder_path, script_path, previous_window=self, selected_option=self.selected_option)

            self.script_upload_window.show()
            #self.script_upload_window = ScriptUploadWindow(folder_path, previous_window=self)
            #self.script_upload_window.show()

    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()

class CoupledUploadWindow(QMainWindow):
    upload_completed = pyqtSignal(str)
    
    def __init__(self, previous_window=None, selected_option=None):
        super().__init__()
        self.previous_window = previous_window
        self.selected_option = selected_option
        self.setWindowTitle("Upload Coupled TDMS Folder")
        self.setGeometry(100, 100, 1050, 750)
        logger.info("Coupled Upload window opened")
        self.showMaximized()
        self.set_background_image(r"Danfoss_BG.png")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.button_upload_folder = QPushButton("Upload Coupled TDMS Folder")
        self.button_upload_folder.clicked.connect(self.upload_coupled_folder)
        self.layout.addWidget(self.button_upload_folder)

        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        self.layout.addWidget(self.button_previous)

    def upload_coupled_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Coupled TDMS Folder")
        if folder_path:
            logger.info(f"Coupled folder uploaded: {folder_path}")
            self.combine_tdms_files(folder_path)
            self.previous_window.update_tdms_file_count(folder_path)
            self.upload_completed.emit(folder_path)
            self.close()
            
            # Determine which script to run based on the selected option
            script_path = r"pcr_rr_new.py" if self.selected_option == "PC RR" else r"piston_group.py"

            self.script_upload_window = ScriptUploadWindow(folder_path, script_path, previous_window=self, selected_option=self.selected_option)
            self.script_upload_window.show()

    def combine_tdms_files(self, folder_path):
        logger.info(f"Combining TDMS files in {folder_path}")
        tdms_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.tdms'):
                    source_path = os.path.join(root, file)
                    dest_path = os.path.join(folder_path, file)
                    if source_path != dest_path:
                        shutil.copy2(source_path, dest_path)
                        logger.info(f"Copied {source_path} to {dest_path}")
                    tdms_files.append(dest_path)
        logger.info(f"Combined {len(tdms_files)} TDMS files in {folder_path}")

    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)
    
    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()
        
        