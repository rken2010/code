@echo off
setlocal

REM Instalador automático para Windows (CMD / PowerShell)
REM Requiere: Python en PATH

set "SCRIPT_DIR=%~dp0"
set "CANDIDATE_1=%SCRIPT_DIR%.."
set "CANDIDATE_2=%SCRIPT_DIR%..\.."
set "PROJECT_ROOT="

for %%I in ("%CANDIDATE_1%") do (
  if exist "%%~fI\pyproject.toml" set "PROJECT_ROOT=%%~fI"
)

if not defined PROJECT_ROOT (
  for %%I in ("%CANDIDATE_2%") do (
    if exist "%%~fI\pyproject.toml" set "PROJECT_ROOT=%%~fI"
  )
)

if not defined PROJECT_ROOT (
  echo [ERROR] No se encontro pyproject.toml cerca del script.
  echo [ERROR] SCRIPT_DIR = %SCRIPT_DIR%
  echo [ERROR] Revisar estructura esperada: repo_root\scripts\install_windows.bat
  exit /b 1
)

pushd "%PROJECT_ROOT%" >nul
if errorlevel 1 (
  echo [ERROR] No se pudo cambiar al directorio del proyecto: %PROJECT_ROOT%
  exit /b 1
)

if not exist "pyproject.toml" (
  echo [ERROR] pyproject.toml no encontrado en: %PROJECT_ROOT%
  popd >nul
  exit /b 1
)

echo [INFO] Proyecto detectado en: %PROJECT_ROOT%

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
