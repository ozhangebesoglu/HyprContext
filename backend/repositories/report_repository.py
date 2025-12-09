"""
Report Repository
~~~~~~~~~~~~~~~~~

Rapor verisi repository implementasyonu.
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Optional

from ..interfaces.repository import IReportRepository
from ..models.report import Report

logger = logging.getLogger(__name__)


class ReportRepository(IReportRepository):
    """Rapor repository (JSON + Markdown dosya tabanlı)."""
    
    def __init__(self, reports_dir: str = "./raporlar"):
        """
        Args:
            reports_dir: Raporlar dizini
        """
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, report: Report) -> str:
        """Rapor kaydet."""
        # ID oluştur
        if not report.id:
            report.id = f"rapor_{report.date.isoformat()}"
        
        # Dosya yollarını belirle
        json_path = self._get_json_path(report.date)
        md_path = self._get_md_path(report.date)
        
        try:
            # JSON olarak kaydet
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
            
            # Markdown olarak kaydet
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(report.content)
            
            return report.id
            
        except Exception as e:
            logger.error(f"Rapor kaydetme hatası: {e}")
            raise
    
    def get_by_date(self, target_date: date) -> Optional[Report]:
        """Tarihe göre rapor getir."""
        json_path = self._get_json_path(target_date)
        
        if not json_path.exists():
            # Sadece MD varsa onu oku
            md_path = self._get_md_path(target_date)
            if md_path.exists():
                return self._read_from_md(md_path, target_date)
            return None
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Report.from_dict(data)
        except Exception as e:
            logger.error(f"Rapor okuma hatası: {e}")
            return None
    
    def get_all(self) -> list[Report]:
        """Tüm raporları getir."""
        reports = []
        
        # JSON dosyalarından oku
        for json_path in sorted(self.reports_dir.glob("rapor_*.json")):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                reports.append(Report.from_dict(data))
            except Exception as e:
                logger.warning(f"Rapor okuma hatası ({json_path}): {e}")
        
        # Sadece MD olanları da ekle (JSON'ı olmayan)
        for md_path in sorted(self.reports_dir.glob("rapor_*.md")):
            json_path = md_path.with_suffix(".json")
            if not json_path.exists():
                try:
                    date_str = md_path.stem.replace("rapor_", "")
                    target_date = date.fromisoformat(date_str)
                    report = self._read_from_md(md_path, target_date)
                    if report:
                        reports.append(report)
                except Exception as e:
                    logger.warning(f"MD rapor okuma hatası ({md_path}): {e}")
        
        return sorted(reports, key=lambda r: r.date)
    
    def export_to_markdown(self, report: Report, path: str) -> bool:
        """Raporu Markdown olarak dışa aktar."""
        try:
            export_path = Path(path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(report.content)
            
            return True
            
        except Exception as e:
            logger.error(f"Markdown export hatası: {e}")
            return False
    
    def _read_from_md(self, md_path: Path, target_date: date) -> Optional[Report]:
        """MD dosyasından rapor oku."""
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            return Report(
                id=f"rapor_{target_date.isoformat()}",
                date=target_date,
                summary="",  # MD'den çıkarılamaz
                content=content
            )
        except Exception:
            return None
    
    def _get_json_path(self, target_date: date) -> Path:
        """Rapor JSON dosya yolunu oluştur."""
        return self.reports_dir / f"rapor_{target_date.isoformat()}.json"
    
    def _get_md_path(self, target_date: date) -> Path:
        """Rapor MD dosya yolunu oluştur."""
        return self.reports_dir / f"rapor_{target_date.isoformat()}.md"
