import sys
import os

def run_init_scripts():
    if getattr(sys, 'frozen', False):
        # Run initialization scripts
        exec(open('pandas_init.py').read())
        exec(open('numpy_init.py').read())
        exec(open('scipy_init.py').read())
        exec(open('matplotlib_init.py').read())

        # Add the directory containing the script to sys.path
        sys.path.insert(0, os.path.dirname(sys.executable))

# Run initialization
run_init_scripts()

# Import and run your main application
import common_main
common_main.main()  # Assuming your main function is called 'main'