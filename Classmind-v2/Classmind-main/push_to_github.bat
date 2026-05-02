@echo off
echo [1/4] Initializing Git...
git init
echo [2/4] Adding Remote...
git remote add origin https://github.com/Satyanderkaushik2004/Classmind
echo [3/4] Committing changes...
git add .
git commit -m "feat: Production-grade email system and UI stabilization"
echo [4/4] Pushing to GitHub...
git branch -M main
git push -u origin main
echo.
echo DONE! Code has been pushed to GitHub.
pause
