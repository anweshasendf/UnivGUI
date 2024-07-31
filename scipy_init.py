import os
import sys

# Ensure scipy can find its resources
if getattr(sys, 'frozen', False):
    os.environ['SCIPY_DATA'] = os.path.join(sys._MEIPASS, 'scipy', 'misc')