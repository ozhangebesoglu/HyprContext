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
    active_window: Optional[str] = None
    screenshot_path: Optional[str] = None
    
    class Config:
        from_attributes = True


class DayData(BaseModel):
    """Günlük veri."""
    day: str
    activities: int


class ActivityStats(BaseModel):
    """Aktivite istatistikleri."""
    total_activities: int
    total_days: int
    today_count: int = 0
    top_tags: list[tuple[str, int]]
    activities_per_day: float
    by_hour: dict[str, int] = {}
    by_day: list[DayData] = []


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
            tags=act.tags,
            active_window=act.active_window,
            screenshot_path=act.screenshot_path
        )
        for act in activities
    ]


@router.get("/today", response_model=list[ActivityResponse])
async def get_today_activities(
    activity_repo=Depends(get_activity_repository)
):
    """Bugünün aktivitelerini getir."""
    from datetime import date as date_module
    
    today = date_module.today()
    activities = activity_repo.get_by_date(today)
    
    return [
        ActivityResponse(
            id=act.id or "",
            timestamp=act.timestamp.isoformat(),
            summary=act.summary,
            tags=act.tags,
            active_window=act.active_window,
            screenshot_path=act.screenshot_path
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
            tags=act.tags,
            active_window=act.active_window,
            screenshot_path=act.screenshot_path
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
        tags=activity.tags,
        active_window=activity.active_window,
        screenshot_path=activity.screenshot_path
    )
