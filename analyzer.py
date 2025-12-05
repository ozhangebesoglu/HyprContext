"""
HyprContext Windows - AI Analiz Modülü
Ollama ile ekran görüntüsü analizi yapar.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

import httpx
from loguru import logger


# Sistem prompt - AI'ın rolünü tanımlar
SYSTEM_PROMPT = """Sen bir masaüstü aktivite analizcisisin. Görevin:

1. Ekran görüntüsünü analiz et
2. Kullanıcının ne yaptığını TÜRKÇE olarak özetle
3. Uygun etiketler ekle

KURALLAR:
- Kısa ve öz ol (1-2 cümle)
- Teknik detayları dahil et (dosya adları, diller, araçlar)
- Format: "Açıklama cümlesi. [Etiket1, Etiket2, Etiket3]"
- Etiketleri MUTLAKA köşeli parantez içinde yaz
- Türkçe yaz"""

# Kullanıcı prompt şablonu
USER_PROMPT_TEMPLATE = """EKRANI ANALİZ ET.

Aktif Pencere: {active_win}
Arka Plan Uygulamaları: {background_apps}
Tespit Edilen Dil: {detected_lang}
Tespit Edilen Dosya: {detected_file}
Geçmiş Aktiviteler (son 3): {history}

FORMAT KURALI:
Cevabın MUTLAKA şu formatta olmalı: "Açıklama cümlesi. [Etiket1, Etiket2]"

ÖRNEKLER:
✅ "VS Code'da main.py dosyası açık, analyze_image fonksiyonu düzenleniyor. [Python, AI, Geliştirme]"
✅ "YouTube'da 'React Tutorial' videosu izleniyor. [YouTube, React, Öğrenme]"
✅ "Terminal'de pip install komutu çalıştırılıyor. [Terminal, Python, Kurulum]"
✅ "Visual Studio'da C# projesi derleniyor. [C#, Visual Studio, Derleme]"

YASAK:
❌ Sadece uygulama listesi yapma
❌ "Genel" etiketi kullanma
❌ Etiket koymayı unutma

ŞİMDİ EKRANA BAK VE YAZ:"""


@dataclass
class AnalysisResult:
    """Analiz sonucu"""
    summary: str
    tags: List[str]
    raw_response: str


class OllamaAnalyzer:
    """Ollama ile görüntü analizi"""
    
    def __init__(self, base_url: str, model: str, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
    
    async def analyze_image_async(
        self,
        image_base64: str,
        active_window: str = "Bilinmiyor",
        background_apps: str = "Yok",
        detected_language: Optional[str] = None,
        detected_file: Optional[str] = None,
        history: str = "Yeni oturum"
    ) -> AnalysisResult:
        """Görüntüyü asenkron analiz et"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await self._do_analysis(
                client, image_base64, active_window, background_apps,
                detected_language, detected_file, history
            )
    
    def analyze_image(
        self,
        image_base64: str,
        active_window: str = "Bilinmiyor",
        background_apps: str = "Yok",
        detected_language: Optional[str] = None,
        detected_file: Optional[str] = None,
        history: str = "Yeni oturum"
    ) -> AnalysisResult:
        """Görüntüyü senkron analiz et"""
        # Prompt oluştur
        user_prompt = USER_PROMPT_TEMPLATE.format(
            active_win=active_window,
            background_apps=background_apps,
            detected_lang=detected_language or "Bilinmiyor",
            detected_file=detected_file or "Yok",
            history=history
        )
        
        # Ollama API isteği
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": user_prompt,
                    "images": [image_base64]
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 150
            }
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            raw_text = data.get("message", {}).get("content", "")
            
            # Sonucu parse et
            summary, tags = self._parse_response(raw_text)
            
            return AnalysisResult(
                summary=summary,
                tags=tags,
                raw_response=raw_text
            )
            
        except httpx.HTTPError as e:
            logger.error(f"Ollama API hatası: {e}")
            return AnalysisResult(
                summary=f"Analiz başarısız: {e}",
                tags=["Hata"],
                raw_response=""
            )
        except Exception as e:
            logger.error(f"Analiz hatası: {e}")
            return AnalysisResult(
                summary=f"Beklenmeyen hata: {e}",
                tags=["Hata"],
                raw_response=""
            )
    
    async def _do_analysis(
        self,
        client: httpx.AsyncClient,
        image_base64: str,
        active_window: str,
        background_apps: str,
        detected_language: Optional[str],
        detected_file: Optional[str],
        history: str
    ) -> AnalysisResult:
        """Asenkron analiz işlemi"""
        user_prompt = USER_PROMPT_TEMPLATE.format(
            active_win=active_window,
            background_apps=background_apps,
            detected_lang=detected_language or "Bilinmiyor",
            detected_file=detected_file or "Yok",
            history=history
        )
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": user_prompt,
                    "images": [image_base64]
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 150
            }
        }
        
        try:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            raw_text = data.get("message", {}).get("content", "")
            
            summary, tags = self._parse_response(raw_text)
            
            return AnalysisResult(
                summary=summary,
                tags=tags,
                raw_response=raw_text
            )
            
        except Exception as e:
            logger.error(f"Async analiz hatası: {e}")
            return AnalysisResult(
                summary=f"Analiz başarısız: {e}",
                tags=["Hata"],
                raw_response=""
            )
    
    def _parse_response(self, text: str) -> Tuple[str, List[str]]:
        """AI yanıtını parse et"""
        text = text.strip()
        
        # Etiketleri çıkar
        tags = self._extract_tags(text)
        
        # Özeti çıkar (etiketler hariç)
        summary = self._extract_summary(text)
        
        # Eğer etiket bulunamadıysa, metinden çıkar
        if not tags:
            tags = self._infer_tags(summary)
        
        return summary, tags
    
    def _extract_tags(self, text: str) -> List[str]:
        """Metinden etiketleri çıkar"""
        # [Etiket1, Etiket2] formatını ara
        match = re.search(r'\[([^\]]+)\]', text)
        if match:
            tags_str = match.group(1)
            tags = [t.strip() for t in tags_str.split(",")]
            return [t for t in tags if t and t.lower() != "genel"]
        
        return []
    
    def _extract_summary(self, text: str) -> str:
        """Metinden özeti çıkar"""
        # Etiketleri kaldır
        summary = re.sub(r'\s*\[[^\]]+\]\s*', '', text)
        
        # Gereksiz karakterleri temizle
        summary = summary.strip()
        summary = re.sub(r'^["\']|["\']$', '', summary)
        summary = re.sub(r'\s+', ' ', summary)
        
        # Çok uzunsa kısalt
        if len(summary) > 200:
            summary = summary[:197] + "..."
        
        return summary if summary else "Aktivite analiz edilemedi"
    
    def _infer_tags(self, text: str) -> List[str]:
        """Metinden etiket çıkar"""
        tags = []
        text_lower = text.lower()
        
        # Uygulama tespiti
        app_keywords = {
            "vs code": "VS Code",
            "vscode": "VS Code",
            "visual studio": "Visual Studio",
            "cursor": "Cursor",
            "sublime": "Sublime Text",
            "notepad": "Notepad++",
            "pycharm": "PyCharm",
            "intellij": "IntelliJ",
            "webstorm": "WebStorm",
            "android studio": "Android Studio",
            "terminal": "Terminal",
            "powershell": "PowerShell",
            "cmd": "CMD",
            "chrome": "Chrome",
            "firefox": "Firefox",
            "edge": "Edge",
            "discord": "Discord",
            "slack": "Slack",
            "teams": "Teams",
            "spotify": "Spotify",
            "youtube": "YouTube",
            "netflix": "Netflix",
            "twitter": "Twitter",
            "reddit": "Reddit",
        }
        
        for keyword, tag in app_keywords.items():
            if keyword in text_lower:
                tags.append(tag)
                break
        
        # Dil tespiti
        lang_keywords = {
            "python": "Python",
            "rust": "Rust",
            "go ": "Go",
            "golang": "Go",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "react": "React",
            "vue": "Vue",
            "angular": "Angular",
            "c#": "C#",
            "c++": "C++",
            "java ": "Java",
            "kotlin": "Kotlin",
            "swift": "Swift",
            "html": "HTML",
            "css": "CSS",
            "sql": "SQL",
        }
        
        for keyword, tag in lang_keywords.items():
            if keyword in text_lower:
                tags.append(tag)
                break
        
        # Aktivite tespiti
        activity_keywords = {
            "kod": "Geliştirme",
            "geliştir": "Geliştirme",
            "düzenl": "Düzenleme",
            "yaz": "Yazma",
            "izl": "İzleme",
            "dinl": "Dinleme",
            "araştır": "Araştırma",
            "öğren": "Öğrenme",
            "test": "Test",
            "debug": "Hata Ayıklama",
            "derle": "Derleme",
            "build": "Derleme",
        }
        
        for keyword, tag in activity_keywords.items():
            if keyword in text_lower:
                tags.append(tag)
                break
        
        # En az bir etiket olsun
        if not tags:
            tags = ["Aktivite"]
        
        return tags[:3]  # Max 3 etiket
    
    def close(self):
        """HTTP client'ı kapat"""
        self.client.close()


# Singleton instance
_analyzer: Optional[OllamaAnalyzer] = None


def get_analyzer(base_url: str, model: str) -> OllamaAnalyzer:
    """Singleton analyzer instance döndür"""
    global _analyzer
    if _analyzer is None or _analyzer.model != model:
        if _analyzer is not None:
            _analyzer.close()
        _analyzer = OllamaAnalyzer(base_url, model)
    return _analyzer


if __name__ == "__main__":
    # Test
    import asyncio
    from capture import take_screenshot_base64
    
    async def test_analyze():
        print("=== Ollama Analiz Testi ===")
        
        # Screenshot al
        b64 = take_screenshot_base64()
        if not b64:
            print("❌ Screenshot alınamadı")
            return
        
        print(f"✓ Screenshot alındı ({len(b64)} karakter)")
        
        # Analiz et
        analyzer = OllamaAnalyzer(
            base_url="http://localhost:11434",
            model="gemma3"
        )
        
        result = await analyzer.analyze_image_async(
            image_base64=b64,
            active_window="test_window | Test Title",
            background_apps="chrome, discord",
            detected_language="Python",
            detected_file="analyzer.py"
        )
        
        print(f"\n📝 Özet: {result.summary}")
        print(f"🏷️  Etiketler: {result.tags}")
        
        analyzer.close()
    
    asyncio.run(test_analyze())


