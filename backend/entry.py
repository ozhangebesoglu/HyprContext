"""
PyInstaller Entry Point
~~~~~~~~~~~~~~~~~~~~~~~

Bu dosya PyInstaller ile derlenirken kullanılır.
Standalone executable olarak çalışır.
"""

import sys
import os
import asyncio
import logging

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    import uvicorn
    
    # Uygulama ayarları
    config = uvicorn.Config(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
    
    server = uvicorn.Server(config)
    
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Sunucu kapatılıyor...")

if __name__ == "__main__":
    main()

