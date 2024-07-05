@echo off

if "%~3" neq "" goto error_arg
if not "%~1"=="" if "%~2"=="" goto error_arg

set "graphviz_zip=%1"
set "pygraphviz_zip=%2"

rmdir .venv /S /Q
python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install --upgrade build

python prepare_graphviz.py ""%graphviz_zip%"" ""%pygraphviz_zip%""

rmdir .venv /S /Q

goto end

:error_arg
echo Error: Incorrect number of arguments.
echo Usage: build.bat ^<Graphviz zip^> ^<PyGraphviz zip^>
exit /b 1

:end
