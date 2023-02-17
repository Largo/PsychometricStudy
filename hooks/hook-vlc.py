from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = collect_dynamic_libs('vlc')

datas = [(binary, '.') for binary in binaries]

# If we are on Mac OS X, add the VLC executable and qt_menu.nib
import sys
if sys.platform == 'darwin':
    from PyInstaller.utils.hooks import get_pyinstaller_path

    vlc_executable = ('/Applications/VLC.app/Contents/MacOS/VLC', '.')
    datas.append(vlc_executable)

    qt_menu_nib = (get_pyinstaller_path('support-files/qt_menu.nib'), 'qt_menu.nib')
    datas.append(qt_menu_nib)
