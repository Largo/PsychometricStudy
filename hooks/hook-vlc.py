# This file adds the VLC dependencies to the binary file.
# Only run if this is wanted

# does not work at the moment

from PyInstaller.utils.hooks import collect_dynamic_libs
from PyInstaller.utils.hooks import collect_data_files
import sys
import vlc
from vlc import EventType

vlc.Instance().media_player_new()


from PyInstaller.utils.hooks import collect_data_files, collect_submodules


datas = []

# If windows
if sys.platform == 'win32':
    print("test")
    # # Find the libvlc.dll file amd add it to the binary
    datas += [
        ('C:\\Program Files\\VideoLAN\\VLC\\libvlc.dll', '.'),
        ('C:\\Program Files\\VideoLAN\\VLC\\libvlccore.dll', '.'),
        ('C:\\Program Files\\VideoLAN\\VLC\\plugins', 'plugins')
    ]

# If Linux
if sys.platform == 'linux':
    # Find the libvlc.so file amd add it to the binary
    binaries = []
    for data in datas:
        if data[0].endswith('libvlc.so'):
            binaries.append(data)
        # also add libvlccore
        if data[0].endswith('libvlccore.so'):
            binaries.append(data)

# If Mac OS X
if sys.platform == 'darwin':
    # Find the libvlc.so file amd add it to the binary
    binaries = []
    for data in datas:
        if data[0].endswith('libvlc.dylib'):
            binaries.append(data)
        # also add libvlccore
        if data[0].endswith('libvlccore.dylib'):
            binaries.append(data)

# binaries = collect_dynamic_libs('vlc')

# datas = [(binary, '.') for binary in binaries]

# If we are on Mac OS X, add the VLC executable and qt_menu.nib
# import sys
if sys.platform == 'darwin':
    print("")
    # vlc_full = ('/Applications/VLC.app/Contents/MacOS/', '.')
    # datas.append(vlc_full)


    #vlc_libs = ('/Applications/VLC.app/Contents/MacOS/lib', '.')
    #datas.append(vlc_libs)
    #vlc_plugin = ('/Applications/VLC.app/Contents/MacOS/plugins', 'libavcodec_plugin.dylib')
    #datas.append(vlc_plugin)
