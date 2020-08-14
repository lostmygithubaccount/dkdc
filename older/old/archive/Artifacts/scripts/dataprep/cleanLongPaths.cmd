@echo off
rem   Removes built long path files that can give errors when deleted via other means.
rem
rem   Using \\?\ prefix requires an absolute path, but enables handling paths greater
rem   than 260 characters long on Windows 10 build greater than 1607 so eventually this
rem   will be all that is needed:
rem   rd /s /q \\?\%cd%\dataprep\Core\LariatSpark\target\scala-2.11
rem   rd /s /q \\?\%cd%\dataprep\Core\LariatSpark\target\streams\$global\assemblyOption\$global\streams\assembly
rem
rem   However we still have Windows Server of older build numbers on build machnines.
rem   Until all are are later Windows builds, we use a workaround: get robocopy to
rem   mirror an empty directory into the directories we wish to be empty but have
rem   long paths under them. It will removes content found there using long path
rem   suported APIs.
rem
pushd %~dp0\..
if exist "%temp%\empty" ( rd /s /q "%temp%\empty" )
mkdir "%temp%\empty"
robocopy /S /PURGE "%temp%\empty" "%cd%\dataprep\Core\LariatSpark\target\scala-2.11" > nul
robocopy /S /PURGE "%temp%\empty" "%cd%\dataprep\Core\LariatSpark\target\streams\$global\assemblyOption\$global\streams\assembly" > nul
popd