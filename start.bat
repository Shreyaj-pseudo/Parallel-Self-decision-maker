@echo off
start cmd /k "cd backend && uvicorn api:app --reload"
start cmd /k "cd frontend && python -m http.server 3000"

rem #http://localhost:3000 is where the local frontend will be served