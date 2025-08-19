@echo off
echo Adding all files...
git add .

echo Creating commit...
git commit -m "Update AvatarMCP with Claude Desktop integration"

echo Force pushing to main branch...
git push -f origin main

echo Done!
pause
