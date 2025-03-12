pip install -r requirements.txt
python -m nuitka --standalone --onefile --disable-ccache --output-dir=build convert.py
