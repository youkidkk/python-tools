@echo off

cd ..

set PYTHONPATH=.

pipenv run python .\ykdpytool\auto_renamer.py D:\Temp

pause
