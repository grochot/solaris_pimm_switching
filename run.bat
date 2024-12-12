@echo off
cd /d "%~dp0"
python -m pip install -r reqirements.txt
python -m pip uninstall pymeasure
python main.py
pause