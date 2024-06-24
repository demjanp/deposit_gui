@echo off
if "%~1"=="" (
	echo Error: Setup file directory not provided.
	echo Usage: scriptname ^<setup file directory^>
	exit /b 1
)

mkdir "%1"

cd ..
rmdir build\dep_gui /S /Q
rmdir dist\deposit_gui /S /Q
call .venv\Scripts\activate.bat
python -m build
call pyinstaller installer_win\dep_gui.spec

python installer_win\make_ifp.py %cd% %1
