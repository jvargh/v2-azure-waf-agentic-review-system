"""Minimal backend bootstrap with defensive guards to diagnose early process exit.
Run with:  python scripts/run_backend_debug.py  (after activating venv)
This bypasses uvicorn's watchdog/reloader and keeps the event loop alive while printing periodic heartbeat.
"""
import uvicorn, asyncio, sys, traceback, os, time

HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
PORT = int(os.getenv("BACKEND_PORT", "8000"))

async def heartbeat():
    while True:
        print(f"[heartbeat] backend alive at http://{HOST}:{PORT}")
        await asyncio.sleep(15)

if __name__ == "__main__":
    print("[debug-start] Launching uvicorn without reload/watch.")
    try:
        config = uvicorn.Config("backend.server:app", host=HOST, port=PORT, reload=False, log_level="debug")
        server = uvicorn.Server(config)
        loop = asyncio.get_event_loop()
        loop.create_task(heartbeat())
        loop.run_until_complete(server.serve())
    except Exception as e:
        print("[debug-error]", type(e).__name__, e)
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("[debug-exit] server.serve() returned; process exiting.")
