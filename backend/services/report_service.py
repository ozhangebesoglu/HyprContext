"""
Report Service
~~~~~~~~~~~~~~

Rapor oluşturma servisi.
Single Responsibility: Sadece rapor oluşturma.
"""

import logging
from datetime import date, datetime
from typing import Optional

from ..interfaces.ai_client import IAIClient
from ..interfaces.repository import IReportRepository, IActivityRepository
from ..models.report import Report

logger = logging.getLogger(__name__)


class ReportService:
    """Rapor oluşturma servisi."""
    
    def __init__(
        self,
        ai_client: IAIClient,
        report_repository: IReportRepository,
        activity_repository: IActivityRepository
    ):
        """
        Args:
            ai_client: AI istemcisi (DIP)
            report_repository: Rapor repository (DIP)
            activity_repository: Aktivite repository (DIP)
        """
        self.ai_client = ai_client
        self.report_repo = report_repository
        self.activity_repo = activity_repository
    
    def generate_report(self, target_date: Optional[date] = None) -> Optional[Report]:
        """Günlük rapor oluştur.
        
        Args:
            target_date: Rapor tarihi (varsayılan: bugün)
            
        Returns:
            Oluşturulan rapor veya None (aktivite yoksa)
        """
        if target_date is None:
            target_date = date.today()
        
        # Aktiviteleri al
        activities = self.activity_repo.get_by_date(target_date)
        
        if not activities:
            logger.warning(f"{target_date} için aktivite bulunamadı")
            return None
        
        # Logları formatla
        log_text = self._format_activities(activities)
        
        # Prompt oluştur
        prompt = self._create_prompt(target_date, log_text, len(activities))
        
        # AI'dan rapor al
        response = self.ai_client.generate(prompt)
        
        # Teknolojileri çıkar
        technologies = self._extract_technologies(activities)
        
        # Rapor objesini oluştur
        report = Report(
            date=target_date,
            summary=self._extract_summary(response),
            content=self._clean_content(response),
            created_at=datetime.now(),
            technologies=technologies,
            activity_count=len(activities),
            raw_logs=log_text
        )
        
        # Kaydet
        report.id = self.report_repo.save(report)
        
        return report
    
    def get_report(self, target_date: date) -> Optional[Report]:
        """Tarihe göre rapor getir."""
        return self.report_repo.get_by_date(target_date)
    
    def get_all_reports(self) -> list[Report]:
        """Tüm raporları getir."""
        return self.report_repo.get_all()
    
    def export_to_obsidian(self, report: Report, path: str) -> bool:
        """Raporu Obsidian'a aktar."""
        return self.report_repo.export_to_markdown(report, path)
    
    def _format_activities(self, activities) -> str:
        """Aktiviteleri formatla."""
        lines = []
        for act in activities:
            lines.append(f"- [{act.get_time()}] {act.summary}")
        return "\n".join(lines)
    
    def _create_prompt(self, target_date: date, log_text: str, count: int) -> str:
        """Rapor prompt'u oluştur."""
        return f"""Logları analiz et ve günlük rapor oluştur.

LOGLAR ({count} kayıt):
{log_text}

ŞABLON:
# 📅 Günlük Rapor: {target_date.isoformat()}

## 🎯 Günün Özeti
(Ana aktiviteler, 2-3 cümle)

## 🛠️ Kullanılan Teknolojiler
(Tespit edilen araçlar, diller - liste halinde)

## ⏱️ Zaman Çizelgesi
(Sabah, öğle, akşam ne yapıldı)

## 💡 Verimlilik Notları
(Odaklanma seviyesi, dikkat dağınıklığı)"""
    
    def _extract_summary(self, response: str) -> str:
        """Yanıttan özeti çıkar."""
        lines = response.split("\n")
        for i, line in enumerate(lines):
            if "Günün Özeti" in line:
                # Sonraki satırları al
                summary_lines = []
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].startswith("#"):
                        break
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                return " ".join(summary_lines)
        return "Günlük aktivite özeti"
    
    def _clean_content(self, response: str) -> str:
        """Yanıtı temizle."""
        marker = "# 📅"
        if marker in response:
            return response[response.find(marker):]
        return response
    
    def _extract_technologies(self, activities) -> list[str]:
        """Aktivitelerden teknolojileri çıkar."""
        tech_set = set()
        
        for act in activities:
            for tag in act.tags:
                # Teknoloji olabilecek etiketler
                if tag.lower() in [
                    "python", "javascript", "typescript", "react", 
                    "node", "rust", "go", "java", "html", "css",
                    "vs code", "terminal", "git", "docker"
                ]:
                    tech_set.add(tag)
        
        return list(tech_set)
