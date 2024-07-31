import os
import sys

def _delvewheel_patch_1_5_4():
    pass

sys.modules['pandas._libs.window.__init__'] = type(sys)('pandas._libs.window.__init__')
sys.modules['pandas._libs.window.__init__'].__file__ = os.path.join(sys.prefix, 'pandas', '_libs', 'window', '__init__.py')