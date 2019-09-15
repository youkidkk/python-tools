@echo off

cd ..

set PYTHONPATH=.

pipenv run python .\ykdpytool\regex_renamer.py D:\Temp config\regex_renamer.conf

pause
