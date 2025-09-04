@echo off
echo ================================================
echo   Predictor de Resistencia de Hormigon v1.0
echo   Iniciando aplicacion...
echo ================================================
echo.

REM Verificar que Python este instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instale Python 3.11+ primero.
    pause
    exit /b 1
)

REM Verificar archivos del modelo
if not exist "modelo_hormigon_ecuador_v1.pkl" (
    echo ERROR: modelo_hormigon_ecuador_v1.pkl no encontrado
    echo Asegurese de ejecutar desde el directorio correcto
    pause
    exit /b 1
)

if not exist "modelo_metadata.json" (
    echo ERROR: modelo_metadata.json no encontrado
    echo Asegurese de ejecutar desde el directorio correcto
    pause
    exit /b 1
)

REM Verificar dependencias principales
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias requeridas...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

REM Ejecutar aplicacion
echo Iniciando interfaz grafica...
python main.py

REM Si la aplicacion se cierra con error
if errorlevel 1 (
    echo.
    echo La aplicacion se cerro con errores.
    echo Revise el archivo concrete_predictor.log para mas detalles.
    pause
)