@if "%_echo%"=="" echo off
setlocal EnableDelayedExpansion
REM cleanup build artifacts and reset source enlistment to a clean state

set _root=%~dp0..
pushd %_root%
echo enlistment root: && cd

set _gulp=node_modules\gulp\bin\gulp.js
if exist %_gulp% (
    echo gulp scorch && node %_gulp% scorch
    echo gulp clean && node %_gulp% clean
)

echo rmdir /s /q target && if exist "target/" (rmdir /s /q target)
echo rmdir /s /q Workbench/target && if exist "Workbench/target/" (rmdir /s /q "Workbench/target/")
echo git checkout . && git checkout .

echo git clean -fdx -e /node_modules && git clean -fdx -e /node_modules

REM On Windows, 'git clean' will remove NTFS junctions/hardlinks created by a previous build
REM This causes the linked file to be removed
REM Running another 'git checkout .' after 'git clean' will restore those removed files
echo git checkout . && git checkout .

echo git gc && git gc

popd
echo Cleanup complete.
