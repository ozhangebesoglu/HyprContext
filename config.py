"""
HyprContext Windows - Konfigürasyon Modülü
Ortam değişkenlerinden ayarları yükler.
"""

from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Uygulama konfigürasyonu"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Ollama Ayarları
    ollama_url: str = Field(default="http://localhost:11434")
    model_vision: str = Field(default="gemma3")
    model_embed: str = Field(default="mxbai-embed-large")
    
    # Zamanlama
    capture_interval: int = Field(default=20, description="Saniye cinsinden yakalama aralığı")
    min_cooldown: int = Field(default=5, description="Minimum bekleme süresi")
    
    # Bellek
    ram_size: int = Field(default=5, description="Kısa süreli bellek boyutu")
    memory_days: int = Field(default=30, description="Veritabanında tutulacak gün sayısı")
    
    # Yasaklı içerik
    banned_keywords: str = Field(
        default="youtube,instagram,twitter,reddit,netflix,tiktok,facebook",
        description="Virgülle ayrılmış yasaklı anahtar kelimeler"
    )
    
    # Odak Ayarları
    distraction_threshold: int = Field(default=3, description="Uyarı için dikkat dağıtıcı eşiği")
    daily_distraction_limit: int = Field(default=1800, description="Günlük dikkat dağıtıcı limiti (saniye)")
    
    # Dosya yolları
    db_path: str = Field(default="hyprcontext.db")
    temp_screenshot_path: str = Field(default="temp_screenshot.png")
    
    @property
    def banned_list(self) -> List[str]:
        """Yasaklı anahtar kelimeleri liste olarak döndür"""
        return [kw.strip().lower() for kw in self.banned_keywords.split(",") if kw.strip()]
    
    @property
    def database_path(self) -> Path:
        """Veritabanı yolunu Path olarak döndür"""
        return Path(self.db_path)
    
    @property
    def screenshot_path(self) -> Path:
        """Screenshot yolunu Path olarak döndür"""
        return Path(self.temp_screenshot_path)
    
    def is_banned(self, text: str) -> bool:
        """Metin yasaklı içerik içeriyor mu?"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.banned_list)


# Global config instance
_config: Config | None = None


def get_config() -> Config:
    """Singleton config instance döndür"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Config'i yeniden yükle"""
    global _config
    _config = Config()
    return _config


if __name__ == "__main__":
    # Test
    config = get_config()
    print(f"Ollama URL: {config.ollama_url}")
    print(f"Vision Model: {config.model_vision}")
    print(f"Capture Interval: {config.capture_interval}s")
    print(f"Banned Keywords: {config.banned_list}")
    print(f"DB Path: {config.database_path}")


