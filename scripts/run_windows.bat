@echo off
setlocal

REM Wrapper para mantener compatibilidad si alguien ejecuta desde /scripts
set "ROOT_SCRIPT=%~dp0..\run_windows.bat"

if not exist "%ROOT_SCRIPT%" (
  echo [ERROR] No se encontro run_windows.bat en la raiz del proyecto.
  exit /b 1
)

call "%ROOT_SCRIPT%"
exit /b %errorlevel%
