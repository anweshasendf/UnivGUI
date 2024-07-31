import os
import sys

def _delvewheel_patch_1_5_1():
    pass

sys.modules['scipy._lib.array_api_compat._aliases'] = type(sys)('scipy._lib.array_api_compat._aliases')
if hasattr(sys, 'frozen'):
    sys.modules['scipy._lib.array_api_compat._aliases'].__file__ = os.path.join(sys.prefix, 'scipy', '_lib', 'array_api_compat', '_aliases.py')