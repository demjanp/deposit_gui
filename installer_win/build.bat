
cd ..
rmdir build\dep_gui /S /Q
rmdir dist\deposit_gui /S /Q
call .venv\Scripts\activate.bat

call pyinstaller installer_win\dep_gui.spec

python installer_win\make_ifp.py %cd%
