@echo off
setlocal

REM Este script debe estar dentro de la carpeta demo_sistema (junto a manage.py)
cd /d "%~dp0"

echo ==========================================
echo   Subiendo cambios a GitHub
echo ==========================================
echo.

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo ERROR: esta carpeta no es un repositorio git, o Git no esta instalado.
    echo Verifica que este archivo este dentro de la carpeta demo_sistema.
    pause
    exit /b 1
)

REM Si git no tiene configurado un autor (nombre/correo), lo configuramos
REM automaticamente solo para este repositorio (no afecta otros proyectos).
git config user.email >nul 2>&1
if errorlevel 1 (
    git config user.email "asesoria.informatica@gmail.com"
    git config user.name "Lennyn"
)

git add -A

git diff --cached --quiet
if not errorlevel 1 (
    echo No hay cambios nuevos para subir.
    pause
    exit /b 0
)

set "mensaje="
set /p mensaje="Escribe una breve descripcion del cambio (o Enter para usar la fecha/hora): "
if "%mensaje%"=="" (
    for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set "fecha=%%a %%b %%c"
    set "mensaje=actualizacion %date% %time%"
)

git commit -m "%mensaje%"
if errorlevel 1 (
    echo.
    echo ERROR al crear el commit. Revisa el mensaje de arriba.
    pause
    exit /b 1
)

echo.
echo Subiendo a GitHub...
git push
if errorlevel 1 (
    echo.
    echo ERROR al subir los cambios. Revisa tu conexion a internet o el mensaje de arriba.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   Listo! Los cambios se subieron a GitHub.
echo   Render va a desplegarlos automaticamente
echo   en unos minutos.
echo ==========================================
echo.
pause
