"""
Analyzer Service
~~~~~~~~~~~~~~~~

AI analiz servisi.
Dependency Inversion: IAIClient interface'ine bağımlı.
"""

import re
import logging
from typing import Optional
from dataclasses import dataclass

from ..interfaces.ai_client import IAIClient
from ..interfaces.capture import WindowInfo

logger = logging.getLogger(__name__)

# Dosya uzantısından programlama dili tespiti
FILE_EXTENSIONS = {
    ".rs": "Rust", ".go": "Go", ".py": "Python",
    ".js": "JavaScript", ".ts": "TypeScript",
    ".tsx": "React/TypeScript", ".jsx": "React/JavaScript",
    ".vue": "Vue.js", ".svelte": "Svelte",
    ".html": "HTML", ".css": "CSS", ".scss": "SCSS",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML", ".md": "Markdown", ".sql": "SQL",
    ".sh": "Shell", ".c": "C", ".cpp": "C++",
    ".java": "Java", ".kt": "Kotlin", ".swift": "Swift",
    ".rb": "Ruby", ".php": "PHP", ".lua": "Lua",
}

# Dikkat dağıtıcı uygulamalar/siteler
DISTRACTIONS = ["youtube", "instagram", "twitter", "reddit", "netflix", "tiktok", "facebook"]

# Sistem prompt'u - HyprContext tanıtımı ve akıllı analiz
SYSTEM_PROMPT = """Sen HyprContext'in akıllı aktivite analistisin.

HyprContext NEDİR:
- Linux masaüstü için üretkenlik takip uygulaması
- Ekran görüntüsü alıp AI ile analiz eder
- Odak süresi takibi yapar
- Dikkat dağıtıcıları tespit eder
- Günlük raporlar oluşturur

GÖREV:
1. Verilen pencere bilgilerini ve ekran görüntüsünü birlikte değerlendir
2. Kullanıcının NE YAPTIĞINI açıkla (sadece "X uygulaması açık" deme)
3. Arka plandaki uygulamaları da değerlendir
4. Dikkat dağıtıcı varsa belirt

YORUM KURALLARI:
- Cursor/VSCode + dosya.go → "Go dili ile X geliştiriyor"
- Cursor/VSCode + dosya.rs → "Rust ile X kodluyor"
- Cursor/VSCode + dosya.py → "Python ile X yazıyor"
- Cursor/VSCode + dosya.tsx → "React/TypeScript ile frontend geliştiriyor"
- YouTube + Tutorial başlığı → "YouTube'da X öğreniyor"
- YouTube + Müzik → "Arka planda müzik dinliyor"
- Terminal aktif → "Terminalde komut çalıştırıyor"
- Aktif kod editörü + arka plan YouTube → "Kodlama yaparken arka planda YouTube açık ⚠️"

FORMAT: Tek cümle açıklama + [Etiket1, Etiket2, Etiket3]
Etiketler: Dil/Teknoloji, Uygulama, Aktivite türü

ÖRNEKLER:
✅ "Cursor'da api.go dosyasını düzenliyor, Go ile REST API geliştiriyor. [Go, Cursor, API Geliştirme]"
✅ "VSCode'da React projesi üzerinde çalışıyor, App.tsx dosyasını düzenliyor. [React, TypeScript, Frontend]"
✅ "Terminalde git komutları çalıştırıyor, commit işlemi yapıyor. [Git, Terminal, Versiyon Kontrol]"
✅ "YouTube'da Rust programlama eğitimi izliyor. [Rust, YouTube, Öğrenme]"
✅ "Cursor'da Python kodu yazarken arka planda Spotify müzik çalıyor. [Python, Cursor, Geliştirme]"

YANLIŞ ÖRNEKLER:
❌ "Cursor uygulaması açık." (çok yüzeysel)
❌ "Ekranda terminal var." (yorum yok)  
❌ "Bir şeyler yapılıyor." (belirsiz)
❌ "VS Code'da Python projesi geliştiriyor." (her seferinde aynı şeyi söyleme, detay ver)

ÖNEMLİ: Her analizde pencere başlığındaki dosya adını, proje adını veya sayfa başlığını kullan!

DİL: Türkçe yaz. ŞİMDİ ANALİZ ET: """


@dataclass
class AnalysisResult:
    """Analiz sonucu."""
    success: bool
    summary: Optional[str] = None
    tags: list[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class AnalyzerService:
    """AI ile aktivite analizi servisi."""
    
    def __init__(self, ai_client: IAIClient):
        """
        Args:
            ai_client: AI istemcisi (DIP - interface'e bağımlı)
        """
        self.ai_client = ai_client
    
    def analyze(
        self, 
        screenshot: bytes, 
        active_window: Optional[WindowInfo],
        all_windows: list[WindowInfo]
    ) -> AnalysisResult:
        """Ekran görüntüsü ve pencere bilgisini analiz et.
        
        Args:
            screenshot: Base64 encoded screenshot
            active_window: Aktif pencere bilgisi
            all_windows: Tüm pencereler
            
        Returns:
            AnalysisResult: Özet ve etiketler
        """
        # Zengin bağlam oluştur
        context = self._create_rich_context(active_window, all_windows)
        
        # Prompt oluştur
        prompt = self._create_prompt(context)
        
        try:
            # AI'dan yanıt al (sistem prompt'u ile)
            response = self.ai_client.generate(prompt, screenshot, system_prompt=SYSTEM_PROMPT)
            
            if not response:
                return AnalysisResult(
                    success=False,
                    error_message="AI boş yanıt döndü"
                )
            
            # Sonucu temizle ve zenginleştir
            cleaned = self._clean_response(response, context)
            
            # Sonucu ayrıştır
            summary = self._extract_summary(cleaned)
            tags = self._extract_tags(cleaned)
            
            # Etiket bulunamadıysa akıllı tahmin
            if not tags:
                tags = self._infer_smart_tags(cleaned, context)
            
            return AnalysisResult(
                success=True,
                summary=summary,
                tags=tags
            )
            
        except Exception as e:
            logger.error(f"Analiz hatası: {e}")
            return AnalysisResult(
                success=False,
                error_message=str(e)
            )
    
    def _create_rich_context(
        self,
        active_window: Optional[WindowInfo],
        all_windows: list[WindowInfo]
    ) -> dict:
        """Zengin bağlam bilgisi oluştur."""
        context = {
            "app_class": "",
            "window_title": "",
            "detected_file": None,
            "detected_language": None,
            "background_apps": [],
            "has_distraction": False,
            "distraction_apps": []
        }
        
        if active_window:
            context["app_class"] = active_window.app_class.lower()
            context["window_title"] = active_window.title
            
            # Dosya ve dil tespiti
            file, lang = self._detect_file_and_language(active_window.title)
            context["detected_file"] = file
            context["detected_language"] = lang
        
        # Arka plan uygulamaları
        if all_windows:
            for window in all_windows:
                app = window.app_class.lower()
                if app not in context["background_apps"]:
                    context["background_apps"].append(app)
                
                # Dikkat dağıtıcı kontrolü
                full_text = f"{app} {window.title}".lower()
                for distraction in DISTRACTIONS:
                    if distraction in full_text:
                        context["has_distraction"] = True
                        if distraction not in context["distraction_apps"]:
                            context["distraction_apps"].append(distraction)
        
        return context
    
    def _detect_file_and_language(self, title: str) -> tuple[Optional[str], Optional[str]]:
        """Pencere başlığından dosya adı ve programlama dili tespit et."""
        for part in title.split(" - "):
            part = part.strip()
            for ext, lang in FILE_EXTENSIONS.items():
                if part.endswith(ext):
                    # Dosya adını bul
                    words = part.split()
                    for word in words:
                        if word.endswith(ext):
                            return word, lang
        return None, None
    
    def _create_prompt(self, context: dict) -> str:
        """Zengin bağlamla analiz prompt'u oluştur."""
        lines = ["PENCERE BİLGİLERİ:"]
        
        if context["app_class"]:
            lines.append(f"AKTİF UYGULAMA: {context['app_class']}")
        if context["window_title"]:
            lines.append(f"PENCERE BAŞLIĞI: {context['window_title']}")
        if context["detected_file"]:
            lines.append(f"AÇIK DOSYA: {context['detected_file']}")
        if context["detected_language"]:
            lines.append(f"PROGRAMLAMA DİLİ: {context['detected_language']}")
        if context["background_apps"]:
            lines.append(f"ARKA PLAN: {', '.join(context['background_apps'][:5])}")
        if context["has_distraction"]:
            lines.append(f"⚠️ DİKKAT DAĞITICI: {', '.join(context['distraction_apps'])}")
        
        if len(lines) == 1:
            lines.append("Pencere bilgisi alınamadı")
        
        lines.append("")
        lines.append("GÖREV: Ekran görüntüsüne ve yukarıdaki bilgilere bakarak kullanıcının ne yaptığını DETAYLI YORUMLA.")
        lines.append("Dosya adını, proje adını veya sayfa başlığını mutlaka kullan!")
        
        return "\n".join(lines)
    
    def _clean_response(self, response: str, context: dict) -> str:
        """Model çıktısını temizle ve zenginleştir."""
        text = response.strip()
        
        # İngilizce giriş cümlelerini temizle
        patterns = [
            "Okay,", "Okay.", "Here's", "Let's analyze", "Based on", "Looking at",
            "**Analysis:**", "**Output:**", "## Analysis", "## Output", "I can see",
            "İşte analiz:", "Analiz:", "**Analiz:**"
        ]
        
        for pattern in patterns:
            if text.startswith(pattern):
                text = text[len(pattern):].strip()
        
        # Markdown temizle
        text = text.replace("**", "").replace("##", "").replace("*", "")
        
        # Satır başı tire/yıldız temizle
        lines = text.split("\n")
        if lines:
            first = lines[0].strip()
            if first.startswith(("-", "•", "–")):
                text = first.lstrip("-•– ").strip()
        
        # İlk anlamlı satırı al
        for line in text.split("\n"):
            line = line.strip()
            if line and len(line) > 20 and not line.startswith(("PENCERE", "AKTİF", "GÖREV")):
                text = line
                break
        
        # Etiket kontrolü
        if "[" not in text or "]" not in text:
            tags = self._infer_smart_tags(text, context)
            text = f"{text.rstrip('.')}. [{', '.join(tags)}]"
        
        return text.strip()
    
    def _format_windows(
        self, 
        active_window: Optional[WindowInfo],
        all_windows: list[WindowInfo]
    ) -> str:
        """Pencere bilgilerini formatla."""
        lines = []
        
        if active_window:
            lines.append(f"Aktif: {active_window.app_class} | {active_window.title}")
        
        if all_windows:
            for window in all_windows[:10]:  # Max 10 pencere
                lines.append(f"- {window.app_class}: {window.title}")
        
        return "\n".join(lines) if lines else "Pencere bilgisi yok"
    
    def _extract_summary(self, response: str) -> str:
        """Yanıttan özeti çıkar."""
        # "[" karakterinden önceki kısım
        if "[" in response:
            return response.split("[")[0].strip()
        return response.strip()
    
    def _extract_tags(self, response: str) -> list[str]:
        """Yanıttan etiketleri çıkar."""
        # [...] içindeki kısım
        match = re.search(r'\[([^\]]+)\]$', response.strip())
        
        if match:
            tag_str = match.group(1)
            tags = [t.strip() for t in tag_str.split(",")]
            return [t for t in tags if t]  # Boşları filtrele
        
        return []
    
    def _infer_smart_tags(self, text: str, context: dict) -> list[str]:
        """Akıllı etiket çıkarımı."""
        tags = []
        
        # 1. Programlama dili (en önemli)
        if context.get("detected_language"):
            tags.append(context["detected_language"])
        else:
            # Metinden dil çıkar
            text_lower = text.lower()
            lang_keywords = [
                ("rust", "Rust"), ("go ", "Go"), ("golang", "Go"),
                ("python", "Python"), ("javascript", "JavaScript"), 
                ("typescript", "TypeScript"), ("react", "React"),
                ("vue", "Vue"), ("svelte", "Svelte"),
            ]
            for kw, lang in lang_keywords:
                if kw in text_lower:
                    tags.append(lang)
                    break
        
        # 2. Uygulama
        app_names = [
            ("cursor", "Cursor"), ("vscode", "VSCode"), ("code", "VSCode"),
            ("terminal", "Terminal"), ("kitty", "Terminal"), ("alacritty", "Terminal"),
            ("firefox", "Firefox"), ("chrome", "Chrome"), ("zen", "Zen Browser"),
            ("obsidian", "Obsidian"), ("notion", "Notion"),
            ("youtube", "YouTube"), ("spotify", "Spotify"), ("discord", "Discord"),
        ]
        
        class_lower = context.get("app_class", "").lower()
        for kw, name in app_names:
            if kw in class_lower:
                tags.append(name)
                break
        
        # 3. Aktivite türü
        text_lower = text.lower()
        if any(k in text_lower for k in ["kodl", "yazıyor", "geliştir", "düzenl"]):
            tags.append("Geliştirme")
        elif any(k in text_lower for k in ["izliyor", "video", "youtube"]):
            tags.append("Video")
        elif any(k in text_lower for k in ["öğren", "tutorial", "eğitim"]):
            tags.append("Öğrenme")
        elif any(k in text_lower for k in ["terminal", "komut", "git"]):
            tags.append("Sistem")
        elif "api" in text_lower:
            tags.append("API")
        
        # En az 1 etiket garanti
        if not tags:
            tags = ["Aktivite"]
        
        return tags[:4]  # Max 4 etiket
    
    def _guess_tags(self, response: str) -> list[str]:
        """Etiket bulunamadıysa metinden tahmin et (eski fonksiyon, uyumluluk için)."""
        return self._infer_smart_tags(response, {})
