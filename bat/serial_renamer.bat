@echo off

cd ..

set PYTHONPATH=.

for /d %%d in (D:\Temp\*) do (
  echo "%%d"
  xcopy "%%d" "%%d_bk" /s/e/i
  pipenv run python .\ykdpytool\serial_renamer.py "%%d"
)

pause
