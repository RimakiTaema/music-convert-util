@echo off
setlocal enabledelayedexpansion

:: Ensure dependencies are installed
python -m pip install --upgrade pip
python -m pip install nuitka

:: Compile the Python script
python -m nuitka --standalone --onefile --disable-ccache --output-dir=build convert.py

:: Rename output file
move build\convert.exe build\convmusic.exe
