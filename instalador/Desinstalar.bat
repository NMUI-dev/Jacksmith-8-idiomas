@echo off
title Desinstalar mod de Jacksmith
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\jacksmith_mod.ps1" -Accion desinstalar
