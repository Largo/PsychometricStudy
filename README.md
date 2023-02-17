# Psychometric Study

(c) 2022 Nathan Ducker - Miyazaki Municipal University 宮崎公立大学（MMU）
If you use this code, please send us a message!

## Installation

### Automatic
pipenv install

### Manual
pip install xlsxwriter
pip install python-vlc
pip install PyQt5
pip install qtawesome
pip install pyinstaller


# How to create an .exe on windows:

pyinstaller --noconsole  app.py --name psychometricstudy --onefile --additional-hooks-dir hooks/ --icon icon.png

For more information see https://realpython.com/pyinstaller-python/