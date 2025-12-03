@echo off
echo Building SLPlayer executable...
python -m PyInstaller SLPlayer.spec
echo.
echo Build complete! Executable is in: dist\SLPlayer\
pause

