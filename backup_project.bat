@echo off
REM Backup script: creates a timestamped backup folder and copies project files
SETLOCAL EnableDelayedExpansion
for /f "tokens=1-5 delims=:-/ " %%d in ("%date% %time%") do (
  set Y=%%f
  set M=%%e
  set D=%%d
)
REM Better timestamp (YYYY_MM_DD_HH_MM_SS)
for /f "tokens=1-4 delims=/:. " %%a in ("%date% %time%") do set TM=%%a_%%b_%%c_%%d
set TIMESTAMP=%date:~6,4%_%date:~3,2%_%date:~0,2%_%time:~0,2%_%time:~3,2%_%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FOLDER=backup_%TIMESTAMP%
mkdir "%BACKUP_FOLDER%"

REM Use ROBOCOPY to mirror while excluding large or virtual env folders
REM Exclude: node_modules, venv, ai_core\venv, frontend\node_modules, backend\node_modules, dist
robocopy "%cd%" "%cd%\%BACKUP_FOLDER%" . /E /COPYALL /R:1 /W:1 /XD node_modules venv ai_core\venv frontend\node_modules backend\node_modules dist .git

echo Backup completed: %BACKUP_FOLDER%
ENDLOCAL
