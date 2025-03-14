@echo off
setlocal enabledelayedexpansion

:: Ensure dependencies are installed
python -m pip install -r requirements.txt

:: Compile the Python script
python setup.py build

:: Rename output file
:: move build\convert.exe build\convmusic.exe
