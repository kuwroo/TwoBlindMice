@echo off
pyinstaller --onefile --clean --windowed ^
--add-data "resources;resources" ^
main.py

pause
