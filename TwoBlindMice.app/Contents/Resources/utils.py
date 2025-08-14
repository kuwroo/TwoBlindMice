import os
import sys

def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS  # When running as .exe
    except Exception:
        base_path = os.path.abspath(".")  # When running as script

    return os.path.join(base_path, relative_path)