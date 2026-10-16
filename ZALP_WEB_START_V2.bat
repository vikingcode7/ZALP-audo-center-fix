@echo off
title ZALP WEB COMMAND CENTER v2.0
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (py zalp_web_command_center_v2.py) else (python zalp_web_command_center_v2.py)
if errorlevel 1 pause
