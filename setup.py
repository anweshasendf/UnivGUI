import sys
import os
from cx_Freeze import setup, Executable
import pymupdf
import pkg_resources
import pandas
import numpy
import scipy
import matplotlib
import sklearn
import statsmodels
import seaborn
import openpyxl
import xlrd
import xlwt

# Increase recursion limit
sys.setrecursionlimit(6000)

pkg_resources_path = pkg_resources.__path__[0]
scipy_path = os.path.dirname(scipy.__file__)
scipy_dlls = [os.path.join(root, file) for root, _, files in os.walk(scipy_path) for file in files if file.endswith('.dll')]
# Manually specify submodules for problematic packages
matplotlib_submodules = [
    'matplotlib.backends',
    'matplotlib.pyplot',
    'matplotlib.figure',
    'matplotlib.axes',
    'matplotlib.lines',
    'matplotlib.patches',
    'matplotlib.text',
    'matplotlib.image',
    'matplotlib.legend',
    'matplotlib.colors',
    'matplotlib.cm',
    'matplotlib.ticker',
    'matplotlib.font_manager',
    'matplotlib.style',
]

scipy_submodules = [
    'scipy._lib.messagestream',
    'scipy.sparse.csgraph._validation',
    'scipy._lib.array_api_compat',
    'scipy.sparse',
    'scipy.sparse.linalg',
    'scipy.sparse.csgraph',
    'scipy.sparse.csr',
    'scipy.sparse.csc',
    'scipy.sparse.lil',
    'scipy.sparse.dok',
    'scipy.sparse.dia',
    'scipy.sparse.bsr',
    'scipy.sparse.construct',
    'scipy.sparse.extract',
]

additional_packages = [
    'numpy', 'scipy', 'matplotlib', 'pandas', 'pymupdf',
    'sklearn', 'statsmodels', 'seaborn', 'openpyxl', 'xlrd', 'xlwt'
]

setup(
    name="GUI_Piston_app_New",
    version="1.0",
    description="Python GUI Based APP for Data Visualization and Data Analysis",
    executables=[Executable("common_main.py")],
    options={
        "build_exe": {
            "packages": additional_packages,
            "includes": matplotlib_submodules + scipy_submodules,
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
                "Upper.png",
                "vcomp140.dll",
                "vcruntime140_1.dll",
                "rtftopdf.py",
                "__init__.py",
                "vcruntime140.dll",
                (pkg_resources_path, "pkg_resources"),
            ] + scipy_dlls,
            "excludes": [
                "tkinter", "unittest", "test", "distutils", "setuptools",
                "matplotlib.tests", "matplotlib.testing"
            ],
            "optimize": 2,
            "include_msvcr": True,
            "zip_include_packages": ["*"],
            "zip_exclude_packages": [],
        }
    }
)