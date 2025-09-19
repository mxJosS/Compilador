@echo off
echo ==============================
echo Instalador de dependencias - Compilador U1
echo ==============================

cd /d "%~dp0"

REM Si no existe venv, lo creamos
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activamos el venv
call venv\Scripts\activate

REM Instalamos dependencias
echo Instalando dependencias necesarias...
pip install --upgrade pip
pip install ply tk emoji

echo.
echo Dependencias instaladas correctamente ✅
pause
