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
        # Prompt oluştur
        prompt = self._create_prompt(active_window, all_windows)
        
        try:
            # AI'dan yanıt al
            response = self.ai_client.generate(prompt, screenshot)
            
            if not response:
                return AnalysisResult(
                    success=False,
                    error_message="AI boş yanıt döndü"
                )
            
            # Sonucu ayrıştır
            summary = self._extract_summary(response)
            tags = self._extract_tags(response)
            
            # Etiket bulunamadıysa tahmin et
            if not tags:
                tags = self._guess_tags(response)
            
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
    
    def _create_prompt(
        self, 
        active_window: Optional[WindowInfo],
        all_windows: list[WindowInfo]
    ) -> str:
        """Analiz prompt'u oluştur."""
        window_text = self._format_windows(active_window, all_windows)
        
        return f"""Ekran görüntüsünü ve pencere bilgilerini analiz et.

PENCERELER:
{window_text}

GÖREV:
1. Kullanıcının ne yaptığını tek cümle ile özetle
2. İlgili etiketleri belirle (en az 2, en fazla 5)

ETİKET KURALLARI:
- Uygulama adı (VS Code, Chrome, vb.)
- Aktivite türü (Kodlama, Araştırma, Video, vb.)
- Teknoloji/Dil (Python, JavaScript, vb.)

FORMAT:
[özet cümlesi] [Etiket1, Etiket2, Etiket3]

ÖRNEK:
VS Code'da Python projesi geliştiriyor. [VS Code, Python, Geliştirme]"""
    
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
    
    def _guess_tags(self, response: str) -> list[str]:
        """Etiket bulunamadıysa metinden tahmin et."""
        response_lower = response.lower()
        tags = []
        
        # Uygulama tespiti
        app_map = {
            "code": "VS Code", "vscode": "VS Code", "cursor": "Cursor",
            "chrome": "Chrome", "firefox": "Firefox", "zen": "Browser",
            "terminal": "Terminal", "obsidian": "Obsidian"
        }
        
        for key, value in app_map.items():
            if key in response_lower:
                tags.append(value)
                break
        
        # Aktivite tespiti
        activity_map = {
            "yazıyor": "Kodlama", "geliştir": "Geliştirme",
            "izliyor": "Video", "araştır": "Araştırma"
        }
        
        for key, value in activity_map.items():
            if key in response_lower:
                tags.append(value)
                break
        
        # En az 1 etiket garanti
        if not tags:
            tags = ["Aktivite"]
        
        return tags
