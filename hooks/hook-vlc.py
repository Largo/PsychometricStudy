# This file adds the VLC dependencies to the binary file.
# Only run if this is wanted

# does not work at the moment

from PyInstaller.utils.hooks import collect_dynamic_libs
import sys

binaries = collect_dynamic_libs('vlc')

datas = [(binary, '.') for binary in binaries]

# If we are on Mac OS X, add the VLC executable and qt_menu.nib
# import sys
if sys.platform == 'darwin':
    vlc_full = ('/Applications/VLC.app/Contents/MacOS/', '.')
    datas.append(vlc_full)
    #vlc_libs = ('/Applications/VLC.app/Contents/MacOS/lib', '.')
    #datas.append(vlc_libs)
    #vlc_plugin = ('/Applications/VLC.app/Contents/MacOS/plugins', 'libavcodec_plugin.dylib')
    #datas.append(vlc_plugin)
