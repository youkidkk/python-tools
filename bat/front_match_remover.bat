@echo off

cd ..

set PYTHONPATH=.
set TARGET_PARENT=D:\Temp
set BACKUPDIR=%TARGET_PARENT%_bk

if exist %BACKUPDIR% (
  echo Error: Backup dir already exists.
  pause
  exit
)
mkdir %BACKUPDIR%

for /d %%d in (%TARGET_PARENT%\*) do (
  echo %%d
  xcopy "%%d" "%BACKUPDIR%\%%~nxd" /s/e/i/q 
  pipenv run python .\ykdpytool\front_match_remover.py "%%d"
)

pause
