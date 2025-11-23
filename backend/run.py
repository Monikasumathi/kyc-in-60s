#!/usr/bin/env python3
"""
KYC-in-60s Backend Server
Run this script to start the FastAPI application
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║         KYC-in-60s Backend Server Starting...           ║
    ║                                                          ║
    ║  Server: http://{host}:{port}                      ║
    ║  Docs:   http://{host}:{port}/docs                 ║
    ║                                                          ║
    ║  Press Ctrl+C to stop the server                        ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

