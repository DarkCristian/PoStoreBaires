@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Instalá Python 3.12 de 64 bits con el launcher py antes de compilar.
  pause
  exit /b 1
)
py -3.12 -m venv .venv
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install -r requirements-build.txt
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m unittest discover -s tests -p "test_*.py" -v
if errorlevel 1 goto error
".venv\Scripts\python.exe" scripts\build.py
if errorlevel 1 goto error
".venv\Scripts\python.exe" scripts\smoke.py
if errorlevel 1 goto error
".venv\Scripts\python.exe" scripts\package.py
if errorlevel 1 goto error
echo Build completo: dist\PoStoreBaires\PoStoreBaires.exe
echo ZIP y SHA256 disponibles en dist.
pause
exit /b 0
:error
echo La compilacion fallo. Revisa el error anterior.
pause
exit /b 1
