
cd ..
rmdir build\dep_gui /S /Q
rmdir dist\deposit_gui /S /Q
call .venv\Scripts\activate.bat

python bin\update_imports.py installer_win

call pyinstaller installer_win\dep_gui.spec

python installer_win\make_nsi.py %cd%
