pip install -r requirements.txt
python -m nuitka --standalone --onefile --disable-ccache --output-dir=build convert.py
mv build/convert build/convmusic
chmod +x build/convmusic
