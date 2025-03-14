from cx_Freeze import setup, Executable

# Replace 'your_script.py' with the name of your Python script
executables = [Executable("convert.py")]

setup(
    name="music-convert-util",
    version="1.0",
    description="Convert Music without doing ffmpeg things",
    executables=executables,
)
