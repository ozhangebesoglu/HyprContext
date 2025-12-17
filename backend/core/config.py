"""
Configuration
~~~~~~~~~~~~~

Uygulama ayarları (pydantic-settings ile).
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


def get_default_data_path() -> str:
    """Varsayılan veri klasörü yolu."""
    # Environment variable öncelikli
    if os.environ.get('HYPRCONTEXT_DATA_PATH'):
        return os.environ['HYPRCONTEXT_DATA_PATH']
    
    # Home dizininde Documents/HyprContext veya HyprContext
    home = Path.home()
    documents = home / 'Documents'
    if documents.exists():
        return str(documents / 'HyprContext')
    return str(home / 'HyprContext')


class Settings(BaseSettings):
    """Uygulama ayarları."""
    
    # Genel
    app_name: str = "HyprContext"
    debug: bool = False
    
    # Veri Klasörü (kullanıcının seçtiği)
    data_path: str = Field(default_factory=get_default_data_path)
    
    # AI Model
    ollama_model: str = "gemma3"
    ollama_embed_model: str = "mxbai-embed-large"
    ollama_base_url: str = "http://localhost:11434"
    
    # Capture
    screenshot_interval: int = 30  # saniye
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    
    # Focus
    daily_distraction_limit_seconds: int = 7200  # 2 saat
    banned_keywords: list[str] = Field(default_factory=lambda: [
        "youtube", "twitter", "reddit", "tiktok", "instagram"
    ])
    
    model_config = {
        "env_prefix": "HYPRCONTEXT_",
        "env_file": ".env",
        "extra": "ignore"
    }
    
    # Dinamik path'ler (data_path'e göre)
    # Not: Bu property'ler her zaman self.data_path'e göre hesaplanır
    # Böylece update_data_path() çağrıldığında otomatik güncellenir
    
    @property
    def screenshots_dir(self) -> str:
        return str(Path(self.data_path) / 'screenshots')
    
    @property
    def screenshot_temp_path(self) -> str:
        return str(Path(self.screenshots_dir) / 'current.png')
    
    @property
    def chroma_db_path(self) -> str:
        return str(Path(self.data_path) / 'hafiza_db')
    
    @property
    def history_jsonl_path(self) -> str:
        return str(Path(self.data_path) / 'history.jsonl')
    
    @property
    def plans_dir(self) -> str:
        return str(Path(self.data_path) / 'planlar')
    
    @property
    def reports_dir(self) -> str:
        return str(Path(self.data_path) / 'raporlar')
    
    @property
    def profile_path(self) -> str:
        return str(Path(self.data_path) / 'profile.yaml')
    
    @property
    def focus_data_path(self) -> str:
        return str(Path(self.data_path) / 'focus_data.json')
    
    def get_profile(self) -> dict:
        """Kullanıcı profilini yükle."""
        profile_path = Path(self.profile_path)
        
        if not profile_path.exists():
            return {}
        
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    
    def update_data_path(self, new_path: str) -> None:
        """Veri klasörü yolunu güncelle."""
        self.data_path = new_path
        # Klasörleri oluştur
        for folder in ['screenshots', 'planlar', 'raporlar', 'hafiza_db']:
            folder_path = Path(new_path) / folder
            folder_path.mkdir(parents=True, exist_ok=True)


# Singleton settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Ayarları al (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Ayarları yeniden yükle."""
    global _settings
    _settings = Settings()
    return _settings
