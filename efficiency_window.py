from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtCore import Qt
import logging
import os 
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
from tdms_window import *

logger = logging.getLogger(__name__)

class EfficiencyWindow(QMainWindow):
    
    option_selected = pyqtSignal(str) 
    
    def __init__(self, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.selected_option = None
        self.setWindowTitle("Efficiency Options")
        self.setGeometry(100, 100, 1050, 750)
        logger.info("Efficiency options window opened")
        self.showMaximized()
        
        self.set_background_image(r"Danfoss_BG.png")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        
        options = ["Efficiency", "LS Hystersis", "LS Linearity", "LS RR", "LS Speed Sweep", "PC Hyst", "PC Speed Sweep", "PC RR"]
        for option in options:
            button = QPushButton(option)
            button.clicked.connect(lambda checked, opt=option: self.select_option(opt))
            self.layout.addWidget(button)

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
        
    def select_option(self, option):
        self.option_selected.emit(option)
        self.close()

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

    
    def open_upload_window(self, option):
        self.option_selected.emit(option)  
        from tdms_window import TDMSTypeWindow
        self.close()
        self.tdms_type_window = TDMSTypeWindow(previous_window=self, selected_option=option)
        self.tdms_type_window.show()

    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()

class HydrostaticWindow(QMainWindow):
    def __init__(self, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("Hydrostatic Options")
        self.setGeometry(100, 100, 1050, 750)
        logger.info("Hydrostatic options window opened")
        self.showMaximized()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        options = ["Null", "Full", "Neutral Deadband"]
        for option in options:
            button = QPushButton(option)
            button.clicked.connect(self.open_upload_window)
            self.layout.addWidget(button)

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
    
    def open_upload_window(self):
        from tdms_window import TDMSTypeWindow
        self.close()
        self.tdms_type_window = TDMSTypeWindow(previous_window=self)
        self.tdms_type_window.show()
        
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