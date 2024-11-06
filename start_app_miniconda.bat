@echo off

CALL conda activate hwtagger-cudnn > nul 2>&1

python pyside6_ui.py

PAUSE