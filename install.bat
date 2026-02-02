@echo off
REM Install PlayLingo in virtualenv and create local run scripts

if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e .

echo Installed playlingo into .venv (editable).

REM Create helper launcher scripts in project root
echo @echo off > run_playlingo.bat
echo call "%%~dp0\.venv\Scripts\activate" >> run_playlingo.bat
echo python -m playlingo.cli %%* >> run_playlingo.bat

echo @echo off > run_playlingo_gui.bat
echo call "%%~dp0\.venv\Scripts\activate" >> run_playlingo_gui.bat
echo python -m playlingo.gui >> run_playlingo_gui.bat

echo Created run_playlingo.bat and run_playlingo_gui.bat in project root.
echo Add project folder to PATH or create shortcuts pointing to these files.
