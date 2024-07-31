from PyInstaller.utils.hooks import collect_data_files, collect_submodules

hiddenimports = collect_submodules('PyQt5')
datas = collect_data_files('PyQt5')