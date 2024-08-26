from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtCore import Qt, QProcess, QTimer
import logging
import sys
import os
import json
import subprocess
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

from script_window import ScriptUploadWindow as EfficiencyScriptUploadWindow
from gui_ndb2_new import ScriptUploadWindow as NDBScriptUploadWindow

logger = logging.getLogger(__name__)

class CommonScriptUploadWindow(QMainWindow):
    def __init__(self, option, folder_path, previous_window=None):
        super().__init__()
        self.option = option
        self.folder_path = folder_path
        self.previous_window = previous_window

        if option in ["Neutral Deadband", "Full Efficiency"]:
            if option == "Full Efficiency":
                script_path = "hst_eff_new.py"
            else:
                script_path = "ndb_test_new.py"
            self.script_window = NDBScriptUploadWindow(data=None, tdms_folder_path=folder_path, script_path=script_path)
        else:
            if option == "PC RR":
                script_path = r"pcr_rr_new.py"
            elif option == "PC Speed Sweep":
                script_path = r"pc_ss.py"  # Add this new condition
            else:
                script_path = r"piston_group.py"
            self.script_window = EfficiencyScriptUploadWindow(folder_path, script_path, previous_window=self)

        self.setCentralWidget(self.script_window)
        self.script_window.show()
        self.logo_layout = QHBoxLayout()
        self.layout.addLayout(self.logo_layout)
                
        self.set_left_logo()
        self.set_right_logo()


    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)
        
    # def set_logo(self):
    #     try:
    #         logo_path = os.path.join(os.path.dirname(__file__), "Danfoss_Logo.png")
    #         if not os.path.exists(logo_path):
    #             print(f"Logo file not found at {logo_path}")
    #             return

    #         logo_label = QLabel()
    #         pixmap = QPixmap(logo_path)
    #         if pixmap.isNull():
    #             print("Failed to load the logo image")
    #             return

    #         scaled_pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    #         logo_label.setPixmap(scaled_pixmap)
    #         logo_label.setStyleSheet("background-color: transparent;")
    #         logo_label.setFixedSize(200, 100) 
            
            
    #         logo_container = QWidget()
    #         logo_container.setFixedSize(self.width(), 120)  
    #         logo_layout = QHBoxLayout(logo_container)
    #         logo_layout.addWidget(logo_label, alignment=Qt.AlignTop | Qt.AlignLeft)
    #         logo_layout.setContentsMargins(20, 20, 0, 0)  # Add some margin to position the logo
            
    #         # Insert the logo container at the top of the main layout
    #         self.layout.insertWidget(0, logo_container)
            
    #         print(f"Logo set successfully from {logo_path}")
    #         print(f"Logo size: {logo_label.size()}")
    #     except Exception as e:
    #         print(f"Error setting logo: {str(e)}")
    
    def set_left_logo(self):
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "Danfoss_Logo.png")
            if not os.path.exists(logo_path):
                print(f"Left logo file not found at {logo_path}")
                return

            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            if pixmap.isNull():
                print("Failed to load the left logo image")
                return

            scaled_pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setStyleSheet("background-color: rgba(255, 255, 255, 128);")
            
            self.logo_layout.addWidget(logo_label, alignment=Qt.AlignLeft | Qt.AlignTop)
            
            print(f"Left logo set successfully from {logo_path}")
            print(f"Left logo size: {logo_label.size()}")
        except Exception as e:
            print(f"Error setting left logo: {str(e)}")

    def set_right_logo(self):
        try:
            # Replace 'path/to/new/logo.png' with the actual path to your new logo
            logo_path = os.path.join(os.path.dirname(__file__), "Upper.png")
            if not os.path.exists(logo_path):
                print(f"Right logo file not found at {logo_path}")
                return

            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            if pixmap.isNull():
                print("Failed to load the right logo image")
                return

            # Make the right logo slightly larger (e.g., 250x125)
            scaled_pixmap = pixmap.scaled(250, 125, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setStyleSheet("background-color: transparent;")
            
            self.logo_layout.addStretch(1)  # Add stretch to push the right logo to the right
            self.logo_layout.addWidget(logo_label, alignment=Qt.AlignRight | Qt.AlignTop)
            
            print(f"Right logo set successfully from {logo_path}")
            print(f"Right logo size: {logo_label.size()}")
        except Exception as e:
            print(f"Error setting right logo: {str(e)}")

