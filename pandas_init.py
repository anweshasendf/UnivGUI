import os
import sys

def _delvewheel_patch_1_5_4():
    pass  # Do nothing

sys.modules['pandas._libs.window.__init__'] = type('Module', (), {})()
os.environ['PANDAS_NUMPY_INSTALLED'] = '1'