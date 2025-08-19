@echo off
echo Initializing git repository...
git init

echo Adding all files...
git add .

echo Creating initial commit...
git commit -m "Initial commit: AvatarMCP with Claude Desktop integration"

echo Adding remote repository...
git remote add origin https://github.com/sandraschi/avatarmcp.git

echo Pushing to GitHub...
git branch -M main
git push -u origin main

echo Done!
pause
