@echo off
pyside6-rcc Resources/resources.py Resources/resources.qrc
python -c "f=open('Resources/resources.py','r',encoding='utf-8').read().replace('from PySide6','from PyQt6').replace('import PySide6','import PyQt6');open('Resources/resources.py','w',encoding='utf-8').write(f)"
echo Conversion done!