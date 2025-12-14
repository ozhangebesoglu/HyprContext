"""
Weather Service
~~~~~~~~~~~~~~~

Hava durumu servisi (wttr.in API).
"""

import logging
import subprocess
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class WeatherData:
    """Hava durumu verisi."""
    location: str
    temperature: str
    condition: str
    humidity: Optional[str] = None
    wind: Optional[str] = None
    emoji: str = "🌡️"
    
    def to_string(self) -> str:
        """Okunabilir format."""
        return f"{self.emoji} {self.condition}, {self.temperature}"
    
    def to_dict(self) -> dict:
        return {
            "location": self.location,
            "temperature": self.temperature,
            "condition": self.condition,
            "humidity": self.humidity,
            "wind": self.wind,
            "emoji": self.emoji,
            "formatted": self.to_string()
        }


class WeatherService:
    """Hava durumu servisi.
    
    Ücretsiz wttr.in API kullanır.
    """
    
    # Önbellek (1 saat geçerli)
    _cache: Optional[WeatherData] = None
    _cache_time: Optional[datetime] = None
    CACHE_DURATION = timedelta(hours=1)
    
    # Hava durumu emoji'leri
    CONDITION_EMOJIS = {
        "sunny": "☀️",
        "clear": "☀️",
        "partly cloudy": "⛅",
        "cloudy": "☁️",
        "overcast": "☁️",
        "fog": "🌫️",
        "mist": "🌫️",
        "rain": "🌧️",
        "light rain": "🌦️",
        "heavy rain": "⛈️",
        "snow": "❄️",
        "thunderstorm": "⛈️",
        "wind": "💨",
    }
    
    def __init__(self, location: str = "Istanbul"):
        """
        Args:
            location: Şehir adı (varsayılan: Istanbul)
        """
        self.location = location
    
    def get_weather(self, force_refresh: bool = False) -> Optional[WeatherData]:
        """Hava durumunu al.
        
        Args:
            force_refresh: Önbelleği yoksay
            
        Returns:
            WeatherData veya None (hata durumunda)
        """
        # Önbellek kontrolü
        if not force_refresh and self._is_cache_valid():
            return self._cache
        
        # API'den al
        weather = self._fetch_from_api()
        
        if weather:
            self._cache = weather
            self._cache_time = datetime.now()
        
        return weather
    
    def _is_cache_valid(self) -> bool:
        """Önbellek geçerli mi?"""
        if self._cache is None or self._cache_time is None:
            return False
        
        return datetime.now() - self._cache_time < self.CACHE_DURATION
    
    def _fetch_from_api(self) -> Optional[WeatherData]:
        """wttr.in API'den hava durumu al."""
        try:
            # curl ile basit request (dependency eklemeden)
            result = subprocess.run(
                ["curl", "-s", f"wttr.in/{self.location}?format=%C+%t+%h+%w"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning(f"wttr.in hatası: {result.stderr}")
                return None
            
            output = result.stdout.strip()
            
            if not output or "Unknown" in output:
                logger.warning(f"wttr.in geçersiz yanıt: {output}")
                return None
            
            # Parse: "Partly cloudy +12°C 65% →10km/h"
            parts = output.split()
            
            # Koşul (ilk kelimeler, sıcaklık öncesi)
            condition_parts = []
            temp_idx = 0
            for i, part in enumerate(parts):
                if part.startswith("+") or part.startswith("-") or "°" in part:
                    temp_idx = i
                    break
                condition_parts.append(part)
            
            condition = " ".join(condition_parts) if condition_parts else "Bilinmiyor"
            temperature = parts[temp_idx] if temp_idx < len(parts) else "?"
            humidity = parts[temp_idx + 1] if temp_idx + 1 < len(parts) else None
            wind = parts[temp_idx + 2] if temp_idx + 2 < len(parts) else None
            
            # Emoji belirle
            emoji = self._get_emoji(condition.lower())
            
            return WeatherData(
                location=self.location,
                temperature=temperature,
                condition=condition,
                humidity=humidity,
                wind=wind,
                emoji=emoji
            )
            
        except subprocess.TimeoutExpired:
            logger.warning("wttr.in timeout")
            return None
        except Exception as e:
            logger.error(f"Hava durumu hatası: {e}")
            return None
    
    def _get_emoji(self, condition: str) -> str:
        """Koşula göre emoji döndür."""
        for key, emoji in self.CONDITION_EMOJIS.items():
            if key in condition:
                return emoji
        return "🌡️"
    
    def clear_cache(self) -> None:
        """Önbelleği temizle."""
        self._cache = None
        self._cache_time = None




