@echo off
rem download.bat [FILENAME] [COM_PORT]
rem Example: download.bat data.csv COM5

rem get user variables, with defaults
set "FILE=%~1"
if "%FILE%"=="" set "FILE=data.csv"
set "PORT=%~2"
if "%PORT%"=="" set "PORT=COM5"

echo Downloading %FILE% from %PORT%

rem download the requested file
mpremote connect %PORT% soft-reset
mpremote connect %PORT% exec "print(open('%FILE%').read())" > %FILE%

echo Finished!