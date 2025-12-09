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


class Settings(BaseSettings):
    """Uygulama ayarları."""
    
    # Genel
    app_name: str = "HyprContext"
    debug: bool = False
    
    # AI Model
    ollama_model: str = "gemma3"
    ollama_embed_model: str = "mxbai-embed-large"
    ollama_base_url: str = "http://localhost:11434"
    
    # Capture
    screenshot_interval: int = 30  # saniye
    screenshot_temp_path: str = "/tmp/hyprcontext_screenshot.png"
    
    # Veritabanı
    chroma_db_path: str = "./hafiza_db"
    history_jsonl_path: str = "./history.jsonl"
    
    # Dosya Yolları
    plans_dir: str = "./planlar"
    reports_dir: str = "./raporlar"
    profile_path: str = "./profile.yaml"
    
    # Focus
    daily_distraction_limit_seconds: int = 7200  # 2 saat
    focus_data_path: str = "./focus_data.json"
    banned_keywords: list[str] = Field(default_factory=lambda: [
        "youtube", "twitter", "reddit", "tiktok", "instagram"
    ])
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    
    model_config = {
        "env_prefix": "HYPRCONTEXT_",
        "env_file": ".env",
        "extra": "ignore"
    }
    
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


@lru_cache()
def get_settings() -> Settings:
    """Ayarları al (cached)."""
    return Settings()
