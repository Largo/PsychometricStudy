# This file adds the VLC dependencies to the binary file.
# Only run if this is wanted

from PyInstaller.utils.hooks import collect_dynamic_libs
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import sys
import vlc
from vlc import EventType

vlc.Instance().media_player_new()

datas = []

# If windows
if sys.platform == 'win32':
    # # Find the libvlc.dll file amd add it to the binary
    datas += [
        ('C:\\Program Files\\VideoLAN\\VLC\\libvlc.dll', '.'),
        ('C:\\Program Files\\VideoLAN\\VLC\\libvlccore.dll', '.'),
        ('C:\\Program Files\\VideoLAN\\VLC\\plugins', 'plugins')
    ]

# If Linux
if sys.platform == 'linux':
    # Find the libvlc.so file amd add it to the binary
    print("missing")

# If Mac OS X
if sys.platform == 'darwin':
    # Find the libvlc files and add it to the binary
    videolanPath = "/Applications/VLC.app/Contents/MacOS"
    datas += [
        #(videolanPath + '/lib/libvlc.dylib', '.'),
        #        (videolanPath + '/lib/libvlc.dylib', '.'),
        (videolanPath + '/lib/*', '.'),
        (videolanPath +  '/plugins', 'plugins')
    ]