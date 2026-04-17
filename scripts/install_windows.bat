@echo off
setlocal

REM Instalador automático para Windows (CMD / PowerShell)
REM Requiere: Python en PATH

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"

pushd "%PROJECT_ROOT%" >nul

python --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python no esta instalado o no esta en PATH.
  popd >nul
  exit /b 1
)

if not exist .venv (
  echo [INFO] Creando entorno virtual .venv en %PROJECT_ROOT%...
  python -m venv .venv
)

echo [INFO] Actualizando pip...
python -m pip install --upgrade pip

echo [INFO] Instalando dependencias del proyecto en %PROJECT_ROOT%...
python -m pip install -e .[dev]

if errorlevel 1 (
  echo [ERROR] Fallo la instalacion de dependencias.
  popd >nul
  exit /b 1
)

echo [OK] Instalacion completa.
echo [INFO] Para ejecutar la API:
echo     .venv\Scripts\python -m uvicorn app.main:app --reload

echo [INFO] Para correr tests:
echo     .venv\Scripts\python -m pytest -q

popd >nul
endlocal
