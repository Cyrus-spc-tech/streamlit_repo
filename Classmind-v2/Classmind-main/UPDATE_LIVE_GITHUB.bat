@echo off
:: Change directory to the script's location
cd /d "%~dp0"

echo [1/4] Checking Git...
if not exist .git (
    echo Initializing Git repository...
    git init
    git remote add origin https://github.com/Satyanderkaushik2004/Classmind
)
echo [2/4] Adding changes...
git add .
echo [3/4] Committing changes...
git commit -m "feat: Fixed Google OAuth and hardened authentication"
echo [4/4] Pushing to GitHub...
git branch -M main
git push -u origin main
echo.
echo ✅ DONE! Changes are now on GitHub. Render will update automatically.
pause
