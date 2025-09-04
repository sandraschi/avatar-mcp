@echo off
powershell -Command "Get-Content -Path 'C:\Users\sandr\AppData\Roaming\Claude\logs\mcp-server-avatarmcp.log' -Tail 20"
pause
