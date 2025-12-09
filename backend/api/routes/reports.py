"""
Reports API
~~~~~~~~~~~

Rapor endpointleri.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ...core.dependencies import get_report_service, get_report_repository

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportResponse(BaseModel):
    """Rapor yanıtı."""
    id: str
    date: str
    summary: str
    content: str
    technologies: list[str]
    activity_count: int
    focus_percentage: Optional[float] = None
    
    class Config:
        from_attributes = True


class ReportListItem(BaseModel):
    """Rapor listesi öğesi."""
    id: str
    date: str
    summary: str
    activity_count: int


class GenerateReportRequest(BaseModel):
    """Rapor oluşturma isteği."""
    date: Optional[str] = None  # YYYY-MM-DD, yoksa bugün


class ExportRequest(BaseModel):
    """Dışa aktarma isteği."""
    path: str  # Obsidian dosya yolu


@router.get("/", response_model=list[ReportListItem])
async def get_reports(
    report_repo=Depends(get_report_repository)
):
    """Tüm raporları getir (özet)."""
    reports = report_repo.get_all()
    
    return [
        ReportListItem(
            id=report.id or "",
            date=report.date.isoformat(),
            summary=report.summary,
            activity_count=report.activity_count
        )
        for report in reports
    ]


@router.get("/today", response_model=ReportResponse)
async def get_today_report(
    report_repo=Depends(get_report_repository)
):
    """Bugünün raporunu getir."""
    today = date.today()
    report = report_repo.get_by_date(today)
    
    if not report:
        raise HTTPException(404, "Bugün için rapor bulunamadı")
    
    return ReportResponse(
        id=report.id or "",
        date=report.date.isoformat(),
        summary=report.summary,
        content=report.content,
        technologies=report.technologies,
        activity_count=report.activity_count,
        focus_percentage=report.focus_percentage
    )


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: GenerateReportRequest,
    report_service=Depends(get_report_service)
):
    """Yeni rapor oluştur."""
    target_date = None
    
    if request.date:
        try:
            target_date = date.fromisoformat(request.date)
        except ValueError:
            raise HTTPException(400, "Geçersiz tarih formatı")
    
    report = report_service.generate_report(target_date)
    
    if not report:
        raise HTTPException(404, "Belirtilen tarih için aktivite bulunamadı")
    
    return ReportResponse(
        id=report.id or "",
        date=report.date.isoformat(),
        summary=report.summary,
        content=report.content,
        technologies=report.technologies,
        activity_count=report.activity_count,
        focus_percentage=report.focus_percentage
    )


@router.post("/{report_date}/export")
async def export_report(
    report_date: str,
    request: ExportRequest,
    report_service=Depends(get_report_service),
    report_repo=Depends(get_report_repository)
):
    """Raporu Obsidian'a aktar."""
    try:
        target_date = date.fromisoformat(report_date)
    except ValueError:
        raise HTTPException(400, "Geçersiz tarih formatı")
    
    report = report_repo.get_by_date(target_date)
    if not report:
        raise HTTPException(404, "Rapor bulunamadı")
    
    success = report_service.export_to_obsidian(report, request.path)
    
    if not success:
        raise HTTPException(500, "Dışa aktarma başarısız")
    
    return {"success": True, "path": request.path}


@router.get("/{report_date}", response_model=ReportResponse)
async def get_report(
    report_date: str,
    report_repo=Depends(get_report_repository)
):
    """Tarihe göre rapor getir."""
    try:
        target_date = date.fromisoformat(report_date)
    except ValueError:
        raise HTTPException(400, "Geçersiz tarih formatı")
    
    report = report_repo.get_by_date(target_date)
    if not report:
        raise HTTPException(404, "Rapor bulunamadı")
    
    return ReportResponse(
        id=report.id or "",
        date=report.date.isoformat(),
        summary=report.summary,
        content=report.content,
        technologies=report.technologies,
        activity_count=report.activity_count,
        focus_percentage=report.focus_percentage
    )
