"""
Activities API
~~~~~~~~~~~~~~

Aktivite endpointleri.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ...core.dependencies import get_activity_repository

router = APIRouter(prefix="/activities", tags=["activities"])


class ActivityResponse(BaseModel):
    """Aktivite yanıtı."""
    id: str
    timestamp: str
    summary: str
    tags: list[str]
    
    class Config:
        from_attributes = True


class ActivityStats(BaseModel):
    """Aktivite istatistikleri."""
    total_activities: int
    total_days: int
    top_tags: list[tuple[str, int]]
    activities_per_day: float


@router.get("/", response_model=list[ActivityResponse])
async def get_activities(
    date: Optional[str] = Query(None, description="YYYY-MM-DD formatında tarih"),
    limit: int = Query(50, ge=1, le=500),
    activity_repo=Depends(get_activity_repository)
):
    """Aktiviteleri getir.
    
    - Tarih belirtilirse o günün aktiviteleri
    - Belirtilmezse son N aktivite
    """
    if date:
        try:
            target_date = date.fromisoformat(date)
            activities = activity_repo.get_by_date(target_date)
        except ValueError:
            raise HTTPException(400, "Geçersiz tarih formatı. YYYY-MM-DD kullanın.")
    else:
        activities = activity_repo.get_recent(limit=limit)
    
    return [
        ActivityResponse(
            id=act.id or "",
            timestamp=act.timestamp.isoformat(),
            summary=act.summary,
            tags=act.tags
        )
        for act in activities
    ]


@router.get("/search")
async def search_activities(
    q: str = Query(..., min_length=2, description="Arama sorgusu"),
    limit: int = Query(10, ge=1, le=50),
    activity_repo=Depends(get_activity_repository)
):
    """Semantik arama yap."""
    activities = activity_repo.search(q, limit=limit)
    
    return [
        ActivityResponse(
            id=act.id or "",
            timestamp=act.timestamp.isoformat() if act.timestamp else "",
            summary=act.summary,
            tags=act.tags
        )
        for act in activities
    ]


@router.get("/stats", response_model=ActivityStats)
async def get_activity_stats(
    activity_repo=Depends(get_activity_repository)
):
    """Aktivite istatistiklerini getir."""
    stats = activity_repo.get_stats()
    return ActivityStats(**stats)


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: str,
    activity_repo=Depends(get_activity_repository)
):
    """ID ile aktivite getir."""
    activity = activity_repo.get_by_id(activity_id)
    
    if not activity:
        raise HTTPException(404, "Aktivite bulunamadı")
    
    return ActivityResponse(
        id=activity.id or "",
        timestamp=activity.timestamp.isoformat(),
        summary=activity.summary,
        tags=activity.tags
    )
