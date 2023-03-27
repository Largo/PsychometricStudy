# Psychometric Study

(c) 2022-2023 Nathan Ducker - Miyazaki Municipal University 宮崎公立大学（MMU）
If you use this code, please send us a message!

## Installation

First install Python 3.11 or newer and VLC 3.0.18 or newer

### Supported Operating Systems
- Windows
- MacOS
- Linux

### Automatic
```
pipenv install
```

### Manual

The following packages are needed. This might administrative permissions.

```
pip install xlsxwriter
pip install python-vlc
pip install PyQt5
pip install qtawesome
pip install pyinstaller
pip install pillow
pip install pyaudio
pip install numpy
```


### Run from source
```
python app.py
```

# How to create an executable file:

Without including VLC in the binary. Will need to have VLC installed. VLC will need to be in the path on Windows.

```
python -m PyInstaller app.py --name PsychometricStudy --onefile --clean --icon icon.ico --add-binary icon.ico
```

Including VLC in the binary. Will work on computers without VLC installed, if you are comfortable with redistributing VLC.

```
python -m PyInstaller --noconsole  app.py --name PsychometricStudy --onefile --additional-hooks-dir hooks --icon icon.ico --add-data="icon.ico;." --clean
```

OSX:

```
python3 -m PyInstaller  --noconsole app.py --name PsychometricStudy --additional-hooks-dir hooks/ --icon icon.png --clean --osx-bundle-identifier=com.idogawa.psychometricstudy --noconfirm

brew install create-dmg
mkdir -p dist/dmg
cp -r "dist/PsychometricStudy.app" dist/dmg
rm dist/PsychometricStudy.dmg
create-dmg \
  --volname "PsychometricStudy" \
  --volicon "icon.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "PsychometricStudy.app" 175 120 \
  --hide-extension "PsychometricStudy.app" \
  --app-drop-link 425 120 \
  "dist/PsychometricStudy.dmg" \
  "dist/dmg/"
```

For more information see https://realpython.com/pyinstaller-python/


## Further Reading on Python Libraries
- https://matiascodesal.com/blog/spice-your-qt-python-font-awesome-icons/
- https://xlsxwriter.readthedocs.io/chart.html
- https://realpython.com/pyinstaller-python/
- https://www.olivieraubert.net/vlc/python-ctypes/doc/vlc-module.html
- https://www.daniweb.com/programming/tutorials/523626/creating-a-gui-wrapper-for-vlc-media-player-in-python-wxpython
- https://www.schemecolor.com/spring-of-red-orange.php
- https://fontawesome.com/v5/search?p=4&o=r&m=free&s=solid

- https://soundeffect-lab.info/sound/button/