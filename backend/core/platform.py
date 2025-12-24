"""
Platform Detection
~~~~~~~~~~~~~~~~~~

Platform-specific utilities for cross-platform support.
"""

import sys
import os
from pathlib import Path


def get_platform() -> str:
    """Return current platform: 'windows', 'linux', or 'darwin'.

    Returns:
        str: Platform identifier
    """
    if sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'darwin'
    return 'linux'


def is_windows() -> bool:
    """Check if running on Windows.

    Returns:
        bool: True if Windows
    """
    return sys.platform == 'win32'


def is_linux() -> bool:
    """Check if running on Linux.

    Returns:
        bool: True if Linux
    """
    return sys.platform.startswith('linux')


def is_macos() -> bool:
    """Check if running on macOS.

    Returns:
        bool: True if macOS
    """
    return sys.platform == 'darwin'


def is_wayland() -> bool:
    """Check if running on Wayland (Linux only).

    Returns:
        bool: True if Wayland session
    """
    if not is_linux():
        return False
    return os.environ.get('XDG_SESSION_TYPE') == 'wayland'


def is_x11() -> bool:
    """Check if running on X11 (Linux only).

    Returns:
        bool: True if X11 session
    """
    if not is_linux():
        return False
    return os.environ.get('XDG_SESSION_TYPE') == 'x11'


def get_default_data_path() -> Path:
    """Get platform-specific default data path.

    Returns:
        Path: Default data directory
        - Windows: Documents/HyprContext
        - Linux/Mac: ~/Documents/HyprContext
    """
    if is_windows():
        # Windows: Use Documents folder
        documents = Path.home() / "Documents"
        if not documents.exists():
            documents = Path.home()
        return documents / "HyprContext"
    else:
        # Linux/Mac
        documents = Path.home() / "Documents"
        if documents.exists():
            return documents / "HyprContext"
        return Path.home() / "HyprContext"


def get_config_path() -> Path:
    """Get platform-specific config path.

    Returns:
        Path: Config directory
        - Windows: %APPDATA%/hyprcontext
        - Linux: ~/.config/hyprcontext
    """
    if is_windows():
        appdata = os.environ.get('APPDATA')
        if appdata:
            return Path(appdata) / "hyprcontext"
        return Path.home() / "AppData" / "Roaming" / "hyprcontext"
    else:
        return Path.home() / ".config" / "hyprcontext"


def get_python_executable() -> str:
    """Get platform-specific Python executable name.

    Returns:
        str: Python executable path/name
    """
    return sys.executable
