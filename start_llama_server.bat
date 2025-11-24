@echo off
echo ========================================
echo Starting llama.cpp server...
echo ========================================
echo.

REM Save current directory
set "PROJECT_DIR=%CD%"

REM Check if llama folder exists
if exist "llama-b7100-bin-win-cpu-x64\llama-server.exe" (
    echo Found llama-server.exe in llama-b7100-bin-win-cpu-x64 folder
    echo Changing to llama directory...
    cd llama-b7100-bin-win-cpu-x64
    echo Starting server with optimized settings...
    echo This may take 1-2 minutes for first response on CPU...
    llama-server.exe -m "%PROJECT_DIR%\models\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf" -c 2048 --port 8080 -t 4 --n-gpu-layers 0
    cd "%PROJECT_DIR%"
    goto :end
)

if exist "llama-server.exe" (
    echo Found llama-server.exe in current directory
    echo Starting server with optimized settings...
    llama-server.exe -m models\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf -c 2048 --port 8080 -t 4 --n-gpu-layers 0
    goto :end
)

REM If not found, show instructions
echo ERROR: llama-server.exe not found!
echo.
echo Please download llama.cpp from:
echo https://github.com/ggerganov/llama.cpp/releases
echo.
echo Extract it to the project folder
echo.
pause

:end
