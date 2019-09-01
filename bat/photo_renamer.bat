@echo off

cd ..

set PYTHONPATH=.

pipenv run python .\ykdpytool\photo_renamer.py D:\Shared D:\Media\Photo\work

pause
