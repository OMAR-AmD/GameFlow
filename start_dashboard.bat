@echo off
echo ==========================================
echo       Lancement de GameFlow AI Engine
echo ==========================================

echo [1/2] Lancement de l'API Python (FastAPI) sur le port 8000...
start cmd /k "python -m uvicorn backend.main:app --reload"

echo [2/2] Lancement de l'interface React (Vite) sur le port 5173...
cd dashboard
start cmd /k "npm run dev"

echo.
echo Les serveurs sont lances dans des fenetres separees.
echo Le tableau de bord sera bientot accessible sur http://localhost:5173
echo Ne fermez pas les fenetres noires pour garder l'IA active.
pause
