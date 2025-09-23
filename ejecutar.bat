@echo off
setlocal
cd /d "%~dp0"

echo ==============================
echo   Compilador U1 - Automatas II
echo ==============================

rem Activa el venv
if exist "venv\Scripts\activate.bat" (
  call "venv\Scripts\activate.bat"
) else (
  echo [!] No se encontro venv\Scripts\activate.bat
  echo     Crea el venv o ajusta la ruta del activate.
  pause
  exit /b 1
)

rem Limpia cache de PLY para evitar tablas viejas
del /q parsetab.py 2>nul
for /d %%D in (__pycache__) do rd /s /q "%%D" 2>nul

rem Verifica Python
python -c "import sys; print('Python', sys.version)" || (
  echo [!] Python no disponible en este entorno.
  pause
  exit /b 1
)

rem Ejecuta la GUI
echo.
echo Lanzando GUI...
python main.py
set ERR=%ERRORLEVEL%

echo.
if %ERR% NEQ 0 (
  echo [!] Hubo un error al ejecutar (arriba veras el traceback).
  pause
) else (
  echo [OK] Proceso finalizado.
  rem Nota: la ventana de Tk se abre y bloquea la consola hasta que la cierres.
  pause
)

endlocal

