"""
run.py — Entry point to start the Lead Scoring API server.

Usage:
    python run.py

Then open:
    http://localhost:8000/docs   ← Swagger UI
    http://localhost:8000/redoc  ← ReDoc UI
"""

import uvicorn
import config as cfg

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════╗
║       X Education — Lead Scoring API  v{cfg.APP_VERSION}         ║
╠══════════════════════════════════════════════════════╣
║  Swagger UI  →  http://{cfg.HOST}:{cfg.PORT}/docs           ║
║  ReDoc       →  http://{cfg.HOST}:{cfg.PORT}/redoc          ║
║  Health      →  http://{cfg.HOST}:{cfg.PORT}/health         ║
╚══════════════════════════════════════════════════════╝
""")
    uvicorn.run(
        "app:app",
        host=cfg.HOST,
        port=cfg.PORT,
        reload=cfg.RELOAD,
        log_level="info",
    )
