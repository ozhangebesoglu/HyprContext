"""
Focus API
~~~~~~~~~

Odak takibi endpointleri.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...core.dependencies import get_focus_service

router = APIRouter(prefix="/focus", tags=["focus"])


class FocusStatsResponse(BaseModel):
    """Odak istatistikleri yanıtı."""
    used_seconds: int
    remaining_seconds: int
    percentage: float
    limit_reached: bool
    formatted_used: str
    formatted_remaining: str
    daily_limit_seconds: int


class FocusCheckResponse(BaseModel):
    """Odak kontrol yanıtı."""
    is_distracted: bool
    found_keyword: str | None = None
    stats: FocusStatsResponse


@router.get("/stats", response_model=FocusStatsResponse)
async def get_focus_stats(
    focus_service=Depends(get_focus_service)
):
    """Odak istatistiklerini getir."""
    stats = focus_service.get_stats()
    
    return FocusStatsResponse(
        used_seconds=stats.used_seconds,
        remaining_seconds=stats.remaining_seconds,
        percentage=stats.percentage,
        limit_reached=stats.is_limit_reached,
        formatted_used=stats.format_used(),
        formatted_remaining=stats.format_remaining(),
        daily_limit_seconds=stats.daily_limit_seconds
    )


@router.get("/check", response_model=FocusCheckResponse)
async def check_focus(
    focus_service=Depends(get_focus_service)
):
    """Anlık odak durumunu kontrol et."""
    is_distracted, keyword = focus_service.check_distraction()
    stats = focus_service.get_stats()
    
    return FocusCheckResponse(
        is_distracted=is_distracted,
        found_keyword=keyword,
        stats=FocusStatsResponse(
            used_seconds=stats.used_seconds,
            remaining_seconds=stats.remaining_seconds,
            percentage=stats.percentage,
            limit_reached=stats.is_limit_reached,
            formatted_used=stats.format_used(),
            formatted_remaining=stats.format_remaining(),
            daily_limit_seconds=stats.daily_limit_seconds
        )
    )


@router.post("/reset")
async def reset_daily(
    focus_service=Depends(get_focus_service)
):
    """Günlük uyarıları sıfırla."""
    focus_service.reset_daily_warnings()
    return {"success": True, "message": "Günlük uyarılar sıfırlandı"}
