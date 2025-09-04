@echo off
echo Starting test at %TIME%
python test_tkinter.py > test_output.log 2>&1
echo Test completed with exit code %ERRORLEVEL%
type test_output.log
pause
