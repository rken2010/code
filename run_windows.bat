@echo off
setlocal

REM Script principal de arranque (debe vivir en la raiz del proyecto)
set "PROJECT_ROOT=%~dp0"

pushd "%PROJECT_ROOT%" >nul

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] No existe .venv. Ejecuta primero install_windows.bat
  popd >nul
  exit /b 1
)

echo [INFO] Iniciando API en http://127.0.0.1:8000
.venv\Scripts\python -m uvicorn app.main:app --reload

popd >nul
endlocal
