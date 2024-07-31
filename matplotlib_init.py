import os
import sys

# Ensure matplotlib can find its data files
if getattr(sys, 'frozen', False):
    import matplotlib
    matplotlib.use('Agg')  # Use non-GUI backend
    matplotlib.rcParams['datapath'] = os.path.join(sys._MEIPASS, 'mpl-data')