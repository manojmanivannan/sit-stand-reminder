from distutils.core import setup # Need this to handle modules
import py2exe 
from datetime import datetime
import easygui
from time import sleep

setup(options = {
                    'py2exe': {
                            'bundle_files': 1, 
                            'compressed': True,
                            'includes': ['easygui'], 
                            }
                },
    windows = [{'script': "sit_stand_reminder.py"}],
    zipfile = None,
    data_files = [('images',["images/sit_down.png","images/stand_up.png","images/walk.png"])],) 

# pyinstaller --onefile --windowed setup.py