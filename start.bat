@echo off
REM start.bat - helper to run PlayLingo CLI or GUI on Windows
IF "%1"=="" (
  echo Usage: start.bat gui ^| translate-srt --input in.srt --output out.srt --src en --dest tr [--field text]
  exit /b 2
)
REM If user wants GUI: start with 'start.bat gui'
IF /I "%1"=="gui" (
  SHIFT
  python -m playlingo.gui %*
  exit /b %ERRORLEVEL%
)
REM forward all args to dotnet run for the PlayLingo project
dotnet run --project "%~dp0src\PlayLingo" -- %*
