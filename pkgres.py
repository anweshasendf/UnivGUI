import pkg_resources
print(pkg_resources.__path__[0])

#pyinstaller --name=GUI_Piston_app --windowed --add-data="users.db;." --add-data="Danfoss_BG.png;." --add-data="Rep24.pdf;." --add-data="TR-054067A.pdf;." --add-data="TR-056054A_NDB.pdf;." --add-data="help_document.pdf;." --add-binary="vcomp140.dll;." --add-binary="vcruntime140_1.dll;." --add-binary="vcruntime140.dll;." --hidden-import=pymupdf --exclude-module=tkinter --add-data="C:\Users\U436445\AppData\Local\Programs\Python\Python311\Lib\site-packages\pkg_resources" *.py
#pyinstaller --name=GUI_Piston_app --windowed "--add-data=users.db;." "--add-data=Danfoss_BG.png;." "--add-data=Rep24.pdf;." "--add-data=TR-054067A.pdf;." "--add-data=TR-056054A_NDB.pdf;." "--add-data=help_document.pdf;." "--add-binary=vcomp140.dll;." "--add-binary=vcruntime140_1.dll;." "--add-binary=vcruntime140.dll;." --hidden-import=pymupdf --exclude-module=tkinter "--add-data=C:\Users\U436445\AppData\Local\Programs\Python\Python311\Lib\site-packages\pkg_resources" common_main.py