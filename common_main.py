import sys
import os
import matplotlib

# Add the parent directory of UnivGUI to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_application_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

application_path = get_application_path()

if application_path not in sys.path:
    sys.path.insert(0, application_path)

def run_init_scripts():
    application_path = get_application_path()

    if getattr(sys, 'frozen', False):
       
        sys.path.insert(0, application_path)

       
        def _delvewheel_patch_1_5_4():
            pass
        sys.modules['pandas._libs.window.__init__'] = type('Module', (), {})()
        os.environ['PANDAS_NUMPY_INSTALLED'] = '1'

        # Numpy initialization
        os.environ['PATH'] = application_path + os.pathsep + os.environ['PATH']

        # Scipy initialization
        os.environ['SCIPY_DATA'] = os.path.join(application_path, 'scipy', 'misc')

      
        # PyQt5 initialization
        os.environ['QT_PLUGIN_PATH'] = os.path.join(application_path, 'PyQt5', 'Qt5', 'plugins')
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(application_path, 'PyQt5', 'Qt5', 'plugins', 'platforms')

run_init_scripts()

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import logging
from PyQt5.QtCore import QObject, QEvent
from common_login import LoginWindow, OptionWindow
from common_choice import EfficiencyWindow, HydrostaticWindow
from tdms_window import TDMSTypeWindow
from gui_ndb2_new import UploadWindow as NDBUploadWindow
from gui_ndb2_new import DisplayHSTEffWindow
from common_upload import CommonScriptUploadWindow
from script_window import *
from display_window import * 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy

class CenterAlignEventFilter(QObject):
    def eventFilter(self, obj, event):
        if isinstance(obj, QPushButton) and event.type() == QEvent.ParentChange:
            QTimer.singleShot(0, lambda: self.centerButton(obj))
        return False

    def centerButton(self, button):
        if button.parent():
            layout = button.parent().layout()
            if layout:
                index = layout.indexOf(button)
                if index != -1:
                    layout.setAlignment(button, Qt.AlignCenter)

class MainApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = None
        self.choice_window = None
        self.option_window = None
        self.upload_window = None
        self.script_upload_window = None
        self.center_align_filter = CenterAlignEventFilter()
        self.app.installEventFilter(self.center_align_filter)
        logger.info("Application started")

    def start(self):
        self.show_login_window()
        return self.app.exec_()

    def show_login_window(self):
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.show_option_window)
        self.login_window.show()
        
    def show_option_window(self):
        self.option_window = OptionWindow()
        self.option_window.efficiency_selected.connect(lambda: self.show_choice_window("Efficiency"))
        self.option_window.hydrostatic_selected.connect(lambda: self.show_choice_window("Hydrostatic"))
        self.option_window.show()

    def show_choice_window(self, choice_type):
        if choice_type == "Efficiency":
            self.choice_window = EfficiencyWindow()
        else:  # Hydrostatic
            self.choice_window = HydrostaticWindow()
        self.choice_window.option_selected.connect(self.show_upload_window)
        self.choice_window.show()

    def show_upload_window(self, option):
        if option == "Neutral Deadband":
            self.upload_window = NDBUploadWindow()
        elif option == "Full Efficiency":
            self.upload_window = NDBUploadWindow(selected_option=option)
            self.upload_window.upload_completed.connect(lambda folder_path: self.show_script_upload_window(option, folder_path))
        else:
            self.upload_window = TDMSTypeWindow(selected_option=option)
            self.upload_window.upload_completed.connect(lambda folder_path: self.show_script_upload_window(option, folder_path))
        
        self.upload_window.show()

    def show_script_upload_window(self, option, folder_path):
        if option == "PC RR":
            script_path = "pcr_rr_new.py"
        elif option == "PC Speed Sweep":
            script_path = "pc_ss.py"
        elif option == "Full Efficiency":
            script_path = "hst_eff_new.py"
        else:
            script_path = "piston_group.py"
        
        self.script_upload_window = ScriptUploadWindow(folder_path, script_path, selected_option=option)
        self.script_upload_window.script_finished.connect(self.show_display_window)
        self.script_upload_window.show()
        

    def show_display_window(self, folder_path, selected_option):
        if selected_option == "PC RR":
            self.display_window = DisplayPCRRWindow(folder_path)
        elif selected_option == "PC Speed Sweep":
            self.display_window = DisplayPCSSWindow(folder_path)  
        elif selected_option == "Full Efficiency":
            self.display_window = DisplayHSTEffWindow(folder_path)
        else:
            self.display_window = DisplayWindow(folder_path)
        self.display_window.show()

if __name__ == "__main__":
    main_app = MainApplication()
    stylesheet = """
    QWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 18px;
        font-weight: bold;
    }
    QPushButton {
        font-size: 20px;
        padding: 8px 16px;
        background-color: #D22B2B;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        width: 450px;
        height: 100px;
        max-width: 450px;
        max-height: 100px;
        min-width: 450px;
        min-height: 100px;
    }
    QPushButton:hover {
        background-color: #C04000;
    }
    QPushButton:pressed {
        background-color: #004275;
    }
    QLabel {
        font-size: 18px;
    }
    QLineEdit {
        font-size: 18px;
        padding: 6px;
        border: 1px solid #BDBDBD;
        border-radius: 4px;
    }
    QTableWidget {
        font-size: 16px;
        gridline-color: #E0E0E0;
    }
    QTableWidget::item {
        padding: 6px;
    }
    QHeaderView::section {
        background-color: #F5F5F5;
        font-weight: bold;
        padding: 8px;
        border: none;
        border-bottom: 1px solid #E0E0E0;
    }
    QMessageBox {
        font-size: 18px;
    }
    QTabWidget::pane {
        border: 1px solid #E0E0E0;
    }
    QTabBar::tab {
        background-color: #F5F5F5;
        padding: 10px 20px;
        border: 1px solid #E0E0E0;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: white;
        border-bottom: 1px solid white;
    }
    """
    main_app.app.setStyleSheet(stylesheet)
    sys.exit(main_app.start())