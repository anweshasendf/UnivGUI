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


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_credentials(user_id, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=? AND password=?", (user_id, password))
    result = cursor.fetchone()
    conn.close()
    return result

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("App launched")
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 1050, 750)
        #self.setFixedSize(950, 650)
        self.set_background_image(r"Danfoss_BG.png")
        self.showMaximized()
        

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.title_label = QLabel("Test Data Automation")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #D22B2B;")
        self.layout.addWidget(self.title_label)


        self.label_user_id = QLabel("User ID")
        self.layout.addWidget(self.label_user_id)
        self.entry_user_id = QLineEdit()
        self.layout.addWidget(self.entry_user_id)

        self.label_password = QLabel("Password")
        self.layout.addWidget(self.label_password)
        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.entry_password)

        self.button_login = QPushButton("Login")
        self.button_login.clicked.connect(self.validate_login)
        self.layout.addWidget(self.button_login)
        
        self.logo_layout = QHBoxLayout()
        self.layout.addLayout(self.logo_layout)
        
        self.set_left_logo()
        self.set_right_logo()
        
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
    #         logo_label.setStyleSheet("background-color: rgba(255, 255, 255, 128);")
            
    #         self.layout.insertWidget(0, logo_label, alignment=Qt.AlignTop | Qt.AlignLeft)
            
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
            
            
    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)

    login_successful = pyqtSignal()
    def validate_login(self):
        user_id = self.entry_user_id.text()
        password = self.entry_password.text()
        logger.info(f"Login attempt: User ID - {user_id}")
        if check_credentials(user_id, password):
            logger.info("Login successful")
            self.login_successful.emit()
            self.close()
            self.option_window = OptionWindow(previous_window=self)
            self.option_window.show()
        else:
            logger.info("Login failed")
            QMessageBox.critical(self, "Error", "Invalid credentials")
    

class OptionWindow(QMainWindow):
    
    efficiency_selected = pyqtSignal()
    hydrostatic_selected = pyqtSignal()
    
    def __init__(self, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("Select Option")
        self.setGeometry(100, 100, 1050, 750)
        logger.info("Option window opened")
        self.showMaximized()
        
        self.set_background_image(r"Danfoss_BG.png")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        
        # self.button_efficiency = QPushButton("Efficiency")
        # self.button_efficiency.clicked.connect(self.open_efficiency_options)
        # self.layout.addWidget(self.button_efficiency)

        # self.button_hydrostatic = QPushButton("Hydrostatic")
        # self.button_hydrostatic.clicked.connect(self.open_hydrostatic_options)
        # self.layout.addWidget(self.button_hydrostatic)
        
        options_layout = QHBoxLayout()

        # Efficiency option
        efficiency_layout = QVBoxLayout()
        efficiency_image = QLabel()
        efficiency_pixmap = QPixmap("PistonBG.png")  # Replace with actual path
        efficiency_image.setPixmap(efficiency_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        efficiency_layout.addWidget(efficiency_image, alignment=Qt.AlignCenter)

        self.button_efficiency = QPushButton("Industrial Piston Pump")
        self.button_efficiency.setFixedSize(350, 100)  # Set fixed size for smaller button
        self.button_efficiency.clicked.connect(self.open_efficiency_options)
        self.button_efficiency.setStyleSheet("""
            QPushButton {
                background-color: #D50000;
                color: white;
                border-radius: 10px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        efficiency_layout.addWidget(self.button_efficiency, alignment=Qt.AlignCenter)
        options_layout.addLayout(efficiency_layout)

        # Add spacing between options
        options_layout.addSpacing(50)

        # Hydrostatic option
        hydrostatic_layout = QVBoxLayout()
        hydrostatic_image = QLabel()
        hydrostatic_pixmap = QPixmap("HydrostatBG.png")  # Replace with actual path
        hydrostatic_image.setPixmap(hydrostatic_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        hydrostatic_layout.addWidget(hydrostatic_image, alignment=Qt.AlignCenter)

        self.button_hydrostatic = QPushButton("Hydrostatic Tests")
        self.button_hydrostatic.setFixedSize(350, 100)  # Set fixed size for smaller button
        self.button_hydrostatic.clicked.connect(self.open_hydrostatic_options)
        self.button_hydrostatic.setStyleSheet("""
            QPushButton {
                background-color: #D50000;
                color: white;
                border-radius: 10px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        hydrostatic_layout.addWidget(self.button_hydrostatic, alignment=Qt.AlignCenter)
        options_layout.addLayout(hydrostatic_layout)

        # Add options layout to main layout
        self.layout.addLayout(options_layout)
        
   

        
        self.button_previous = QPushButton("Previous")
        self.button_previous.setFixedSize(280, 80)  # Set fixed size for smaller button
        self.button_previous.clicked.connect(self.go_to_previous_window)
        self.button_previous.setStyleSheet("""
            QPushButton {
                background-color: #D50000;
                color: white;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        self.layout.addWidget(self.button_previous, alignment=Qt.AlignCenter)
        
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



    def open_efficiency_options(self):
        from common_choice import EfficiencyWindow
        self.close()
        self.efficiency_window = EfficiencyWindow(previous_window=self)
        self.efficiency_window.show()

    def open_hydrostatic_options(self):
        from common_choice import HydrostaticWindow
        self.close()
        self.hydrostatic_window = HydrostaticWindow(previous_window=self)
        self.hydrostatic_window.show()

    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()