@if "%_echo%"=="" echo off
setlocal ENABLEDELAYEDEXPANSION
REM find and launch python exe that comes with az CLI v2

REM oh the fun one can have with CMD: capture the output of: 'where az'
for /F "tokens=*" %%p in ('where -f az') do (set _az=%%p)

if !%_az%! EQU !! (echo ERROR: prereq az CLI v2 is not installed locally! && exit /b 1)

call :getPath %_az%
call %_pyPath% %*
exit /b %ERRORLEVEL%

:getPath
    set _pyPath="%~dp1..\python"
    exit /b 0