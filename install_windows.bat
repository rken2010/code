@echo off
setlocal

REM Script principal de instalacion (debe vivir en la raiz del proyecto)
set "PROJECT_ROOT=%~dp0"

pushd "%PROJECT_ROOT%" >nul

if not exist "pyproject.toml" (
  echo [ERROR] Este script debe ejecutarse desde la raiz del proyecto.
  echo [ERROR] No se encontro pyproject.toml en %PROJECT_ROOT%
  popd >nul
  exit /b 1
)

python --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python no esta instalado o no esta en PATH.
  popd >nul
  exit /b 1
)

if not exist .venv (
  echo [INFO] Creando entorno virtual .venv...
  python -m venv .venv
)

echo [INFO] Actualizando pip...
python -m pip install --upgrade pip

echo [INFO] Instalando dependencias del proyecto...
python -m pip install -e .[dev]

if errorlevel 1 (
  echo [ERROR] Fallo la instalacion de dependencias.
  popd >nul
  exit /b 1
)

echo [OK] Instalacion completa.

popd >nul
endlocal
