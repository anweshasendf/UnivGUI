import sys
from cx_Freeze import setup, Executable
import pymupdf
import pkg_resources
import pandas
import numpy
import matplotlib
import os 
import scipy 
from PyQt5 import QtCore
import PyQt5
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import reportlab
import nptdms
import sqlite3
import logging

pkg_resources_path = pkg_resources.__path__[0]


# Increase recursion limit
sys.setrecursionlimit(5000)

# Define the packages to include
packages_to_include = [
    "numpy", "pandas", "pymupdf", "matplotlib", "scipy",
    "numpy.core", "numpy.lib", "numpy.linalg",
    "pandas.core", "pandas.io", "pandas.plotting",
    "matplotlib.backends", "matplotlib.pyplot", "matplotlib.figure",
    "scipy.integrate", "scipy.optimize", "scipy.stats",
    "pytz", "dateutil", "six",
    "PyQt5", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets",
    "matplotlib", "matplotlib.backends", "matplotlib.figure",
    "matplotlib.text", "matplotlib.axes", "matplotlib.lines",
    "matplotlib.patches", "matplotlib.path", "matplotlib.cm",
    "matplotlib.colors", "matplotlib.collections", "matplotlib.ticker",
    "matplotlib.font_manager", "matplotlib.image", "matplotlib.legend",
    "matplotlib.mathtext", "matplotlib.spines", "matplotlib.style",
    "matplotlib.textpath", "matplotlib.transforms", "matplotlib.tri",
    "scipy.integrate", "scipy.optimize", "scipy.stats", "scipy.signal",
    "scipy.interpolate", 
    "PyQt5", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets",
    "sklearn.linear_model", "mplcursors", "nptdms","reportlab","sqlite3"
]


pyqt_dir = os.path.dirname(PyQt5.__file__)
qt_dir = os.path.join(pyqt_dir, "Qt5")

def include_qt_files():
    files = []
    for root, _, filenames in os.walk(qt_dir):
        for filename in filenames:
            files.append((os.path.join(root, filename), os.path.relpath(os.path.join(root, filename), qt_dir)))
    return files

qt_files = include_qt_files()


application_path = os.path.dirname(os.path.abspath(__file__))


os.environ['QT_PLUGIN_PATH'] = os.path.join(application_path, 'PyQt5', 'Qt5', 'plugins')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(application_path, 'PyQt5', 'Qt5', 'plugins', 'platforms')


python_dir = os.path.dirname(sys.executable)



setup(
    name="GUI_Piston_app_New",
    version="1.0",
    description="Python GUI Based APP for Data Visualization and Data Analysis",
    executables=[Executable("common_main.py", base="Win32GUI")],
    options={
        "build_exe": {
            "packages": packages_to_include,
            "includes": [
                "pandas._libs.tslibs.base",
                "pandas._libs.tslibs.np_datetime",
                "numpy.core._methods",
                "numpy.lib.format",
                "scipy.sparse.csgraph._validation",
                "scipy.special._ufuncs_cxx",
                "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets",
                "PyQt5.sip"
            ],
            "include_files": [
                "common_choice.py",
                "common_login.py",
                "common_main.py",
                "common_scripting.py",
                "common_upload.py",
                "Danfoss_BG.png",
                "Danfoss_BG2.png",
                "Danfoss_Logo.png",
                "display_window.py",
                "efficiency_window.py",
                "gui_ndb2_new.py",
                "guipdf_ndb.py",
                "guipdf.py",
                "hst_eff_new.py",
                "Rep24.pdf",
                "HydrostatBG.png",
                "PistonBG.png",
                "pcr_rr_new.py",
                "script_window.py",
                "setup_2.py",
                "setup_db.py",
                "setup.py",
                "tdms_window.py",
                "tdmsreader_new.py",
                "help_document.pdf",
                "insert_user.py",
                "logger.py",
                "login_window.py",
                "ndb_test_new.py",
                "piston_group.py",
                "piston_single.py",
                "sitecustomize.py",
                "users.db",
                "pandas_init.py",
                "Upper.png",
                "vcomp140.dll",
                "vcruntime140_1.dll",
                "rtftopdf.py",
                "pandas_init.py",
                "numpy_init.py",
                "scipy_init.py",
                "matplotlib_init.py",
                "__init__.py",
                "vcruntime140.dll",
                (os.path.join(python_dir, "python3.dll"), "python3.dll"),
                (os.path.join(python_dir, "vcruntime140.dll"), "vcruntime140.dll"),
                (pkg_resources_path, "pkg_resources"),
                (numpy.get_include(), "numpy"),
                (matplotlib.get_data_path(), "mpl-data"),
                
            ] +  qt_files,
            "excludes": ["tkinter"],
            "optimize": 2,
            "include_msvcr": True,
        }
    }
)