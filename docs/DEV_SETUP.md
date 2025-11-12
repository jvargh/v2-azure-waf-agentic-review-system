# Development Setup

## Quick Start

Start both services concurrently:

```powershell
npm run dev
```
Backend (FastAPI) and frontend (Vite) run in parallel.

Ports:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

Press `Ctrl+C` to stop both processes.

## Individual Commands

### Backend Only
```powershell
npm run backend
```

### Frontend Only
```powershell
npm run frontend
```

## Prerequisites

1. **Python Environment**: Ensure `venv` is activated and dependencies installed:
   ```powershell
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Node.js Dependencies**:
   ```powershell
   npm install          # Root dependencies (concurrently)
   cd frontend
   npm install          # Frontend dependencies
   ```

3. **MongoDB** (Optional): Install MongoDB locally or use in-memory fallback.
   - If MongoDB is running on `mongodb://localhost:27017`, backend will persist data.
   - Otherwise, backend falls back to in-memory storage (data cleared on restart).

## Connection Status

Top‑right badge:
- Green "Connected": API reachable
- Red "Offline" / "Reconnecting": Backend not responding (check terminal or visit http://localhost:8000/api/health)

Click badge to recheck immediately.

## Troubleshooting

### Backend won't start
- Activate venv: `\.\venv\Scripts\Activate.ps1`
- Install deps: `pip install -r requirements.txt`

### Frontend shows backend disconnected
- Verify backend logs in terminal (cyan-prefixed lines)
- Check http://localhost:8000/api/health in browser (should return JSON with `mongo_connected`)

### Port conflicts
- Backend uses port 8000
- Frontend uses port 3000
- Change ports in `package.json` if needed.

## Project Structure

```
.
├── backend/           # FastAPI server
│   ├── server.py      # Main API endpoints
│   └── app/           # Agents, tools, analysis modules
├── frontend/          # React UI
│   └── src/
│       ├── components/
│       ├── context/
│       └── api/
├── venv/              # Python virtual environment
└── package.json       # Root dev scripts
```

## Next Steps

1. Navigate to http://localhost:3000
2. Create a new assessment
3. Upload architecture documents, diagrams, or support case CSVs
4. Start analysis to evaluate against all 5 Well-Architected pillars
