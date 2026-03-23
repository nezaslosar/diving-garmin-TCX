# diving-garmin-TCX
Simple desktop app for generating Garmin-compatible TCX files for scuba dive activities

Designed for divers who want a quick, manual way to log dives into Garmin Connect when direct import is not available or practical.

---

## Features

- Slovenian 🇸🇮 and English 🇬🇧 interface
- Language selection on startup
- Calendar date picker
- Time selection (hours + minutes)
- Duration and weight input
- MET-based calorie estimation
- Adjustable dive conditions:
  - water temperature (cold)
  - effort level
  - current intensity (none / moderate / strong)
- Automatic `.tcx` file generation
- Compatible with Garmin Connect import

---

## Run from Python

### 1. Install dependency

bash
pip install tkcalendar

### 2. Run the app
python dive_garmin.py

### 3. Create Windows executable (.exe)
Install PyInstaller: pip install pyinstaller

Build the app: pyinstaller --onefile --windowed --icon=ikona.ico dive_garmin.py

Find your executable: dist/dive_garmin.exe

You can move the .exe file anywhere (e.g. Desktop) and run it without Python.

How to use
1. Open the app
2. Select your language
3. Enter dive data:
  - date
  - start time
  - duration
  - body weight
  - MET level
  - dive conditions
4. Click "Create TCX file"
5. The file is saved automatically to your Downloads folder
6. Upload it to Garmin Connect (web)

### 4. Import into Garmin Connect
1. Go to Garmin Connect (web)
2. Click Import Data
3. Upload the generated .tcx file

## Notes
  - Activities will appear as "Other" in Garmin Connect
  - You can manually rename them to "Diving"
  - The app focuses on:
    - duration
    - calorie estimation
    - simple logging workflow

## Why this app?

Some dive computers and logging apps do not provide a simple way to export data into Garmin Connect.

This app provides a lightweight workaround:
  - manually enter key dive data
  - generate a compatible .tcx file
  - import it into Garmin in seconds

## Requirements
- Python 3.10+
- tkcalendar

