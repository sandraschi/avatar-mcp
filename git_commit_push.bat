@echo off
echo Adding all files to git...
git add .

echo.
echo Committing changes...
git commit -m "Update AvatarMCP with Claude Desktop integration and VRM support"

echo.
echo Pushing to remote repository...
git push

echo.
echo Done!
pause
