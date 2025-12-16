#!/usr/bin/env python3
"""
HyprContext Backend Packager
----------------------------
PyInstaller ile backend'i standalone executable olarak paketler.
"""

import subprocess
import sys
import shutil
from pathlib import Path

def main():
    root = Path(__file__).parent.parent
    backend_dir = root / "backend"
    dist_dir = root / "frontend" / "backend-dist"
    
    # PyInstaller spec
    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{backend_dir / "main.py"}'],
    pathex=['{root}'],
    binaries=[],
    datas=[
        ('{root / "profile.yaml"}', '.'),
        ('{root / "focus_data.json"}', '.'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'backend.api',
        'backend.api.routes',
        'backend.api.websocket',
        'backend.core',
        'backend.services',
        'backend.adapters',
        'backend.repositories',
        'backend.models',
        'backend.interfaces',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='hyprcontext-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
'''
    
    spec_file = root / "backend.spec"
    spec_file.write_text(spec_content)
    
    print("PyInstaller ile backend paketleniyor...")
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file)
    ], cwd=root)
    
    if result.returncode != 0:
        print("PyInstaller başarısız!")
        sys.exit(1)
    
    # dist/hyprcontext-backend'i frontend/backend-dist'e kopyala
    src = root / "dist" / "hyprcontext-backend"
    if src.exists():
        dist_dir.mkdir(parents=True, exist_ok=True)
        dest = dist_dir / "hyprcontext-backend"
        if dest.exists():
            dest.unlink()
        shutil.copy2(src, dest)
        print(f"Backend kopyalandı: {dest}")
    
    # Temizlik
    spec_file.unlink(missing_ok=True)
    shutil.rmtree(root / "build", ignore_errors=True)
    shutil.rmtree(root / "dist", ignore_errors=True)
    
    print("✅ Backend paketleme tamamlandı!")

if __name__ == "__main__":
    main()
