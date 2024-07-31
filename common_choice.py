import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QGridLayout, QLabel, QTextEdit

from PyQt5.QtCore import Qt
import logging
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtCore import Qt
import sqlite3
import logging
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
import os 
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QTextEdit



from tdms_window import TDMSTypeWindow
from gui_ndb2_new import UploadWindow as NDBUploadWindow
from common_upload import CommonScriptUploadWindow
from PyQt5.QtWidgets import QScrollArea


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
        
        self.add_legend()
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        
        
        grid_layout = QGridLayout()
        
        options = ["Efficiency", "LS Hystersis", "LS Linearity", "LS RR", "LS Speed Sweep", "PC Hyst", "PC Speed Sweep", "PC RR"]
        row, col = 0, 0
        for option in options:
            button = QPushButton(option)
            button.clicked.connect(lambda checked, opt=option: self.select_option(opt))
            grid_layout.addWidget(button, row, col)
            col += 1
            if col > 3:  # Adjust this value to change the number of columns
                col = 0
                row += 1

        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        #self.layout.addWidget(self.button_previous)
        grid_layout.addWidget(self.button_previous, row + 1, 2, 1, 2)

        
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        
        self.layout.addLayout(grid_layout)

        self.logo_layout = QHBoxLayout()
        self.layout.addLayout(self.logo_layout)
                
        self.set_left_logo()
        self.set_right_logo()
        
    def add_legend(self):
        legend_text = "LS = Low Speed\nPC = Pressure Compensator"
        legend_box = QTextEdit()
        legend_box.setPlainText(legend_text)
        legend_box.setReadOnly(True)
        legend_box.setFixedSize(300, 60)  # Adjust size as needed
        legend_box.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #D50000;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        self.layout.addWidget(legend_box, alignment=Qt.AlignCenter)
            
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


    def select_option(self, option):
        self.selected_option = option
        self.option_selected.emit(option)
        self.open_upload_window(option)
        
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
    
    option_selected = pyqtSignal(str) 
    
    def __init__(self, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("Hydrostatic Options")
        self.setGeometry(100, 100, 1050, 750)
        logger.info("Hydrostatic options window opened")
        self.showMaximized()
        self.selected_option = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        options = ["Null", "Full Efficiency", "Neutral Deadband"]
        for option in options:
            button = QPushButton(option)
            button.clicked.connect(lambda _, opt=option: self.open_upload_window(opt))
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
        
    def select_option(self, option):
        self.option_selected.emit(option)
        self.close()
    
    def open_upload_window(self, option):
        if option == "Neutral Deadband":
            self.upload_window = NDBUploadWindow(previous_window=self, selected_option=option)
        elif option == "Full Efficiency":
            self.upload_window = NDBUploadWindow(previous_window=self, selected_option=option)
        else:
            self.upload_window = TDMSTypeWindow(previous_window=self, selected_option=option)
        
        self.upload_window.upload_completed.connect(lambda folder_path: self.open_script_upload_window(option, folder_path))
        self.upload_window.show()
        self.close()
        
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
            
    def open_script_upload_window(self, option, folder_path):
        if option == "Full Efficiency":
            script_path = "hst_eff_new.py"
        elif option == "Neutral Deadband":
            script_path = "ndb_test_new.py"
        else:
            script_path = "ndb_test_new.py"  # Default script

        self.script_upload_window = CommonScriptUploadWindow(folder_path, script_path, previous_window=self, selected_option=option)
        self.script_upload_window.show()
        self.close()
    