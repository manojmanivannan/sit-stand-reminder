# Sit Stand Reminder

A simple python application to remind you take breaks while working

## Description

This application cycles through 3 modes every 30 minutes. At the start of the hour, it reminds you to sit. After 20 minutes, it reminds you to stand. After 8 minutes, it reminds you to walk and after 2 more minutes, it reminds you to sit again.
1. Sit   - 20 minutes
2. Stand -  8 minutes
3. Walk  -  2 minutes

## Getting Started
To install this, you need to generate an exe file either using py2exe or PyInstaller. You can install it using `pip install py2exe` or `pip install pyinstaller`

### Installing
#### Using PyInstaller (recommended)

* `pyinstaller --clean sit_stand_reminder.spec`

#### Using py2exe
* `python setup.py py2exe`

### Downloading the Artifact
You can directly get the latest exe file from the releases page or from below 

[sit-stand-reminder.exe](https://github.com/manojmanivannan/sit-stand-reminder/releases/download/0.0.12/sit_stand_reminder.exe)

### Executing program

Either case, your exe will be generated under `dist` folder under the project directory. You can create a shortcut and place this in your windows start up folder.

Alternatively, you create a .bat file with contents `start "" "path\to\exe\file_name.exe` and create a shortcut of it and place in under your windows start up folder

