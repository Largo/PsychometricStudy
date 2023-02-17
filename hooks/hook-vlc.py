from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = collect_dynamic_libs('vlc')

datas = [(binary, '.') for binary in binaries]

