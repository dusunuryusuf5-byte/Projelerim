@echo off
REM start.bat - helper to run PlayLingo CLI on Windows
IF "%1"=="" (
  echo Usage: start.bat translate-srt --input in.srt --output out.srt --src en --dest tr [--field text]
  exit /b 2
)
REM forward all args to dotnet run for the PlayLingo project
dotnet run --project "%~dp0src\PlayLingo" -- %*
