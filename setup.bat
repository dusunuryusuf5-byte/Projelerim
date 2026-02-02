@echo off
REM Setup PlayLingo environment on Windows
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Setup complete. Activate with: .venv\Scripts\activate
