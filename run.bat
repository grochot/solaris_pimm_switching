@echo off
cd /d "%~dp0"
python -m pip3 install -r requirements.txt
python -m pip3 uninstall pymeasure
python main.py