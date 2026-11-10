echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="D:\ANSYS Inc\v222\fluent/ntbin/win64/winkill.exe"

"D:\ANSYS Inc\v222\fluent\ntbin\win64\tell.exe" DESKTOP-KUJ9RI4 57213 CLEANUP_EXITING
if /i "%LOCALHOST%"=="DESKTOP-KUJ9RI4" (%KILL_CMD% 5684) 
if /i "%LOCALHOST%"=="DESKTOP-KUJ9RI4" (%KILL_CMD% 23500) 
if /i "%LOCALHOST%"=="DESKTOP-KUJ9RI4" (%KILL_CMD% 15948)
del "C:\Users\A320N\Documents\ChatGPT\MMME3086 cw1\solver\native_figures_2026-11-10\cleanup-fluent-DESKTOP-KUJ9RI4-23500.bat"
