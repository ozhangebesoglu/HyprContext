"""
Plan Service
~~~~~~~~~~~~

Plan oluşturma servisi.
Single Responsibility: Sadece plan oluşturma.
"""

import logging
from datetime import date, datetime
from typing import Optional

from ..interfaces.ai_client import IAIClient
from ..interfaces.repository import IPlanRepository, IActivityRepository
from ..models.plan import Plan
from .weather_service import WeatherService

logger = logging.getLogger(__name__)


class PlanService:
    """Plan oluşturma servisi."""
    
    def __init__(
        self,
        ai_client: IAIClient,
        plan_repository: IPlanRepository,
        activity_repository: IActivityRepository,
        profile: dict,
        weather_service: Optional[WeatherService] = None
    ):
        """
        Args:
            ai_client: AI istemcisi (DIP)
            plan_repository: Plan repository (DIP)
            activity_repository: Aktivite repository (DIP)
            profile: Kullanıcı profili
            weather_service: Hava durumu servisi (opsiyonel)
        """
        self.ai_client = ai_client
        self.plan_repo = plan_repository
        self.activity_repo = activity_repository
        self.profile = profile
        self.weather_service = weather_service
    
    def generate_plan(
        self,
        user_note: Optional[str] = None,
        active_course: Optional[str] = None,
        weather: Optional[str] = None
    ) -> Plan:
        """Günlük plan oluştur.
        
        Args:
            user_note: Kullanıcı notu
            active_course: Aktif kurs (manuel override)
            weather: Hava durumu
            
        Returns:
            Oluşturulan plan
        """
        today = date.today()
        
        # Aktif kursu belirle
        if not active_course:
            active_course = self._get_active_course()
        
        # Hava durumunu al (manuel verilmediyse otomatik)
        if not weather and self.weather_service:
            weather_data = self.weather_service.get_weather()
            if weather_data:
                weather = weather_data.to_string()
        
        if not weather:
            weather = "Bilinmiyor"
        
        # Son aktiviteleri al
        recent_activities = self.activity_repo.get_recent(limit=50)
        activity_summary = self._summarize_activities(recent_activities)
        
        # Prompt oluştur
        prompt = self._create_prompt(
            today=today,
            weather=weather,
            user_note=user_note or "Yok",
            active_course=active_course,
            activity_summary=activity_summary
        )
        
        # AI'dan plan al
        response = self.ai_client.generate(prompt)
        
        # Plan objesini oluştur
        plan = Plan(
            date=today,
            mission=self._extract_mission(response),
            content=self._clean_content(response),
            created_at=datetime.now(),
            weather=weather,
            active_course=active_course,
            user_note=user_note
        )
        
        # Kaydet
        plan.id = self.plan_repo.save(plan)
        
        return plan
    
    def get_plan(self, target_date: date) -> Optional[Plan]:
        """Tarihe göre plan getir."""
        return self.plan_repo.get_by_date(target_date)
    
    def update_plan(self, plan: Plan) -> bool:
        """Planı güncelle."""
        plan.updated_at = datetime.now()
        return self.plan_repo.update(plan)
    
    def get_all_plans(self) -> list[Plan]:
        """Tüm planları getir."""
        return self.plan_repo.get_all()
    
    def _get_active_course(self) -> str:
        """Profil'den aktif kursu bul."""
        try:
            courses = self.profile.get("egitim_programi", {}).get("durum", [])
            for course in courses:
                if "Aktif" in course.get("durum", ""):
                    return course["isim"]
        except Exception:
            pass
        return "Genel Gelişim"
    
    def _summarize_activities(self, activities) -> str:
        """Aktiviteleri özetle."""
        if not activities:
            return "Geçmiş aktivite verisi yok."
        
        lines = []
        for act in activities[-20:]:  # Son 20
            lines.append(f"- [{act.get_date()} {act.get_time()}] {act.summary}")
        
        return "\n".join(lines)
    
    def _create_prompt(
        self,
        today: date,
        weather: str,
        user_note: str,
        active_course: str,
        activity_summary: str
    ) -> str:
        """Plan prompt'u oluştur."""
        return f"""Bugünün planını oluştur.

VERİLER:
- Tarih: {today.isoformat()}
- Hava: {weather}
- Kullanıcı Notu: {user_note}
- Aktif Eğitim/Odak: {active_course}
- Geçmiş Aktiviteler:
{activity_summary}

KURAL: "{active_course}" konusuna odaklan.

ŞABLON:
# 🎯 Günün Misyonu: [Tek cümle hedef]
> **Hava:** {weather}
> **Odak:** {active_course}

## 🌅 Sabah (09:00 - 12:00)
* [Saat]: [Görev]

## ☀️ Öğle (13:00 - 17:00)
* [Saat]: [Görev]

## 🌙 Akşam (18:00 - 22:00)
* [Saat]: [Görev]

## ⚠️ Asistan Notu
[Kısa motivasyon notu]"""
    
    def _extract_mission(self, response: str) -> str:
        """Yanıttan misyonu çıkar."""
        for line in response.split("\n"):
            if "Günün Misyonu:" in line:
                return line.split(":", 1)[-1].strip()
        return "Bugünü verimli geçir"
    
    def _clean_content(self, response: str) -> str:
        """Yanıtı temizle."""
        # "# 🎯" ile başlayan kısımdan itibaren al
        marker = "# 🎯"
        if marker in response:
            return response[response.find(marker):]
        return response
