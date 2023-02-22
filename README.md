# Psychometric Study

(c) 2022 Nathan Ducker - Miyazaki Municipal University 宮崎公立大学（MMU）
If you use this code, please send us a message!

## Installation

### Automatic
```
pipenv install
```

### Manual
```
pip install xlsxwriter
pip install python-vlc
pip install PyQt5
pip install qtawesome
pip install pyinstaller
```


### Run from source
```
python app.py
```

# How to create an executable file:

Without including VLC in the binary. Will need to have VLC installed. VLC will need to be in the path on Windows.

```
pyinstaller --noconsole  app.py --name PsychometricStudy --onefile --clean
```

Including VLC in the binary. Will work on computers without VLC installed, but is potentially problematic

```
pyinstaller --noconsole  app.py --name PsychometricStudy --onefile --additional-hooks-dir hooks/ --icon icon.png --clean
```

For more information see https://realpython.com/pyinstaller-python/