@echo off
pip install -r requirements.txt
Invoke-WebRequest -Uri "https://github.com/Nuitka/DependnecyWalker/releases/latest/download/depends.exe" -OutFile "$env:TEMP\depends.exe"
         New-Item -ItemType Directory -Path "$env:LocalAppData\Nuitka\Nuitka\Cache\downloads\depends\x86_64" -Force
mv build/convert.exe build/convmusic.exe
