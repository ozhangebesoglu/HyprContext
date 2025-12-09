"""
Plan Repository
~~~~~~~~~~~~~~~

Plan verisi repository implementasyonu.
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Optional

from ..interfaces.repository import IPlanRepository
from ..models.plan import Plan

logger = logging.getLogger(__name__)


class PlanRepository(IPlanRepository):
    """Plan repository (JSON dosya tabanlı)."""
    
    def __init__(self, plans_dir: str = "./planlar"):
        """
        Args:
            plans_dir: Planlar dizini
        """
        self.plans_dir = Path(plans_dir)
        self.plans_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, plan: Plan) -> str:
        """Plan kaydet."""
        from datetime import datetime
        
        # ID oluştur
        if not plan.id:
            plan.id = f"plan_{plan.date.isoformat()}"
        
        # Dosya yolunu belirle
        file_path = self._get_file_path(plan.date)
        
        # JSON olarak kaydet
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(plan.to_dict(), f, ensure_ascii=False, indent=2)
            
            # Markdown olarak da kaydet
            md_path = file_path.with_suffix(".md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(plan.content)
            
            return plan.id
            
        except Exception as e:
            logger.error(f"Plan kaydetme hatası: {e}")
            raise
    
    def get_by_date(self, target_date: date) -> Optional[Plan]:
        """Tarihe göre plan getir."""
        file_path = self._get_file_path(target_date)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Plan.from_dict(data)
        except Exception as e:
            logger.error(f"Plan okuma hatası: {e}")
            return None
    
    def get_all(self) -> list[Plan]:
        """Tüm planları getir."""
        plans = []
        
        for file_path in sorted(self.plans_dir.glob("plan_*.json")):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                plans.append(Plan.from_dict(data))
            except Exception as e:
                logger.warning(f"Plan okuma hatası ({file_path}): {e}")
        
        return plans
    
    def update(self, plan: Plan) -> bool:
        """Plan güncelle."""
        file_path = self._get_file_path(plan.date)
        
        if not file_path.exists():
            logger.warning(f"Güncellenecek plan bulunamadı: {plan.date}")
            return False
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(plan.to_dict(), f, ensure_ascii=False, indent=2)
            
            # Markdown'ı da güncelle
            md_path = file_path.with_suffix(".md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(plan.content)
            
            return True
            
        except Exception as e:
            logger.error(f"Plan güncelleme hatası: {e}")
            return False
    
    def delete(self, target_date: date) -> bool:
        """Plan sil."""
        file_path = self._get_file_path(target_date)
        md_path = file_path.with_suffix(".md")
        
        try:
            if file_path.exists():
                file_path.unlink()
            if md_path.exists():
                md_path.unlink()
            return True
        except Exception as e:
            logger.error(f"Plan silme hatası: {e}")
            return False
    
    def _get_file_path(self, target_date: date) -> Path:
        """Plan dosya yolunu oluştur."""
        return self.plans_dir / f"plan_{target_date.isoformat()}.json"
