"""
HyprContext Windows - Pencere Bilgisi Modülü
Windows API kullanarak aktif pencere ve tüm pencere bilgilerini toplar.
"""

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from typing import List, Optional
from loguru import logger

# Windows API tanımları
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Callback tipi
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


@dataclass
class WindowInfo:
    """Pencere bilgisi"""
    hwnd: int
    title: str
    process_name: str
    class_name: str
    is_visible: bool
    
    def __str__(self) -> str:
        return f"{self.process_name} | {self.title}"


@dataclass
class WindowContext:
    """Pencere bağlam bilgisi - AI analizi için"""
    app_name: str
    window_title: str
    detected_language: Optional[str]
    detected_file: Optional[str]
    background_apps: List[str]
    has_distraction: bool


def get_window_text(hwnd: int) -> str:
    """Pencere başlığını al"""
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def get_class_name(hwnd: int) -> str:
    """Pencere sınıf adını al"""
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buffer, 256)
    return buffer.value


def get_process_name(hwnd: int) -> str:
    """Pencere işlem adını al"""
    try:
        import psutil
        
        # Process ID al
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        # Process adını al
        process = psutil.Process(pid.value)
        return process.name().replace(".exe", "")
    except Exception:
        return "unknown"


def is_window_visible(hwnd: int) -> bool:
    """Pencere görünür mü?"""
    return bool(user32.IsWindowVisible(hwnd))


def get_foreground_window() -> Optional[WindowInfo]:
    """Aktif pencereyi al"""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None
    
    title = get_window_text(hwnd)
    class_name = get_class_name(hwnd)
    process_name = get_process_name(hwnd)
    
    return WindowInfo(
        hwnd=hwnd,
        title=title,
        process_name=process_name,
        class_name=class_name,
        is_visible=True
    )


def get_all_windows() -> List[WindowInfo]:
    """Tüm görünür pencereleri al"""
    windows: List[WindowInfo] = []
    
    def enum_callback(hwnd: int, _: int) -> bool:
        if is_window_visible(hwnd):
            title = get_window_text(hwnd)
            # Boş başlıklı veya sistem pencerelerini atla
            if title and not title.startswith("MSCTFIME"):
                class_name = get_class_name(hwnd)
                process_name = get_process_name(hwnd)
                
                # Bazı sistem pencerelerini filtrele
                skip_classes = ["Shell_TrayWnd", "Progman", "WorkerW", "Button"]
                if class_name not in skip_classes:
                    windows.append(WindowInfo(
                        hwnd=hwnd,
                        title=title,
                        process_name=process_name,
                        class_name=class_name,
                        is_visible=True
                    ))
        return True
    
    callback = EnumWindowsProc(enum_callback)
    user32.EnumWindows(callback, 0)
    
    return windows


def get_active_window_string() -> str:
    """Aktif pencere bilgisini string olarak döndür"""
    window = get_foreground_window()
    if window:
        return f"{window.process_name} | {window.title}"
    return "Bilinmiyor"


def get_background_apps_string() -> str:
    """Arka plan uygulamalarını string olarak döndür"""
    active = get_foreground_window()
    all_windows = get_all_windows()
    
    if not all_windows:
        return "Yok"
    
    # Aktif pencere hariç diğer uygulamaları listele
    active_hwnd = active.hwnd if active else 0
    background = [
        w.process_name for w in all_windows 
        if w.hwnd != active_hwnd
    ]
    
    # Benzersiz uygulamalar
    unique_apps = list(dict.fromkeys(background))[:10]  # Max 10 uygulama
    
    if not unique_apps:
        return "Yok"
    
    return ", ".join(unique_apps)


def detect_programming_language(title: str) -> Optional[str]:
    """Pencere başlığından programlama dilini tespit et"""
    language_patterns = {
        # Dosya uzantıları
        ".py": "Python",
        ".rs": "Rust",
        ".go": "Go",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".jsx": "React",
        ".tsx": "React/TypeScript",
        ".vue": "Vue",
        ".svelte": "Svelte",
        ".html": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".toml": "TOML",
        ".md": "Markdown",
        ".sql": "SQL",
        ".sh": "Shell",
        ".bash": "Bash",
        ".zsh": "Zsh",
        ".ps1": "PowerShell",
        ".c": "C",
        ".cpp": "C++",
        ".h": "C/C++ Header",
        ".hpp": "C++ Header",
        ".cs": "C#",
        ".java": "Java",
        ".kt": "Kotlin",
        ".swift": "Swift",
        ".rb": "Ruby",
        ".php": "PHP",
        ".lua": "Lua",
        ".zig": "Zig",
        ".nim": "Nim",
        ".ex": "Elixir",
        ".exs": "Elixir Script",
        ".erl": "Erlang",
        ".hs": "Haskell",
        ".ml": "OCaml",
        ".fs": "F#",
        ".clj": "Clojure",
        ".r": "R",
        ".jl": "Julia",
        ".dart": "Dart",
    }
    
    title_lower = title.lower()
    for ext, lang in language_patterns.items():
        if ext in title_lower:
            return lang
    
    return None


def detect_file_name(title: str) -> Optional[str]:
    """Pencere başlığından dosya adını tespit et"""
    import re
    
    # Yaygın dosya pattern'leri
    patterns = [
        r"([a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+)",  # file.ext
        r"([a-zA-Z0-9_\-]+\.rs)",  # Rust
        r"([a-zA-Z0-9_\-]+\.py)",  # Python
        r"([a-zA-Z0-9_\-]+\.go)",  # Go
        r"([a-zA-Z0-9_\-]+\.js)",  # JavaScript
        r"([a-zA-Z0-9_\-]+\.ts)",  # TypeScript
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def check_distraction(process_name: str, title: str, banned_keywords: List[str]) -> bool:
    """Dikkat dağıtıcı içerik var mı kontrol et"""
    combined = f"{process_name} {title}".lower()
    return any(keyword in combined for keyword in banned_keywords)


def get_window_context(banned_keywords: List[str]) -> WindowContext:
    """Tam pencere bağlam bilgisi döndür"""
    active = get_foreground_window()
    all_windows = get_all_windows()
    
    if not active:
        return WindowContext(
            app_name="Bilinmiyor",
            window_title="",
            detected_language=None,
            detected_file=None,
            background_apps=[],
            has_distraction=False
        )
    
    # Arka plan uygulamaları
    active_hwnd = active.hwnd
    background = list(dict.fromkeys([
        w.process_name for w in all_windows 
        if w.hwnd != active_hwnd
    ]))[:10]
    
    # Dikkat dağıtıcı kontrolü - tüm pencerelerde
    has_distraction = False
    for window in all_windows:
        if check_distraction(window.process_name, window.title, banned_keywords):
            has_distraction = True
            break
    
    return WindowContext(
        app_name=active.process_name,
        window_title=active.title,
        detected_language=detect_programming_language(active.title),
        detected_file=detect_file_name(active.title),
        background_apps=background,
        has_distraction=has_distraction
    )


def check_any_distraction(banned_keywords: List[str]) -> Optional[str]:
    """Herhangi bir pencerede yasaklı içerik var mı?"""
    # Önce aktif pencere
    active = get_foreground_window()
    if active:
        combined = f"{active.process_name} {active.title}".lower()
        for keyword in banned_keywords:
            if keyword in combined:
                return keyword
    
    # Tüm pencereler
    all_windows = get_all_windows()
    for window in all_windows:
        combined = f"{window.process_name} {window.title}".lower()
        for keyword in banned_keywords:
            if keyword in combined:
                return keyword
    
    return None


if __name__ == "__main__":
    # Test
    print("=== Aktif Pencere ===")
    active = get_foreground_window()
    if active:
        print(f"  Başlık: {active.title}")
        print(f"  Process: {active.process_name}")
        print(f"  Class: {active.class_name}")
    
    print("\n=== Tüm Pencereler ===")
    for window in get_all_windows()[:5]:
        print(f"  {window.process_name}: {window.title[:50]}...")
    
    print("\n=== Pencere Bağlamı ===")
    ctx = get_window_context(["youtube", "netflix"])
    print(f"  App: {ctx.app_name}")
    print(f"  Dil: {ctx.detected_language}")
    print(f"  Dosya: {ctx.detected_file}")
    print(f"  Arka plan: {ctx.background_apps}")
    print(f"  Dikkat dağıtıcı: {ctx.has_distraction}")


