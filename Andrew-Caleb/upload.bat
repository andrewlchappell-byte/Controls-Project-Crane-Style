@echo off
echo Preparing upload...
python preload.py

echo Uploading...
mpremote connect COM5 run load.py

echo Finished!