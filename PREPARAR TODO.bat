@echo off
rem Descarga de una vez todo lo necesario para COMPILAR el mod / downloads everything needed to BUILD the mod.
rem Para JUGAR no hace falta / not needed to PLAY: use the Releases zip.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\preparar_todo.ps1" %*
pause
