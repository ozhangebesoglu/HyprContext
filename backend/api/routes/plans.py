"""
Plans API
~~~~~~~~~

Plan endpointleri.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ...core.dependencies import get_plan_service, get_plan_repository

router = APIRouter(prefix="/plans", tags=["plans"])


class PlanTask(BaseModel):
    """Plan görevi."""
    time: str
    description: str
    completed: bool = False


class PlanResponse(BaseModel):
    """Plan yanıtı."""
    id: str
    date: str
    mission: str
    content: str
    tasks: list[PlanTask]
    completion_rate: float
    weather: Optional[str] = None
    active_course: Optional[str] = None
    
    class Config:
        from_attributes = True


class CreatePlanRequest(BaseModel):
    """Plan oluşturma isteği."""
    user_note: Optional[str] = None
    active_course: Optional[str] = None
    weather: Optional[str] = None


class UpdatePlanRequest(BaseModel):
    """Plan güncelleme isteği."""
    content: str
    mission: Optional[str] = None


@router.get("/", response_model=list[PlanResponse])
async def get_plans(
    plan_repo=Depends(get_plan_repository)
):
    """Tüm planları getir."""
    plans = plan_repo.get_all()
    
    return [
        PlanResponse(
            id=plan.id or "",
            date=plan.date.isoformat(),
            mission=plan.mission,
            content=plan.content,
            tasks=[PlanTask(time=t.time, description=t.description, completed=t.completed) for t in plan.tasks],
            completion_rate=plan.get_completion_rate(),
            weather=plan.weather,
            active_course=plan.active_course
        )
        for plan in plans
    ]


@router.get("/today", response_model=PlanResponse)
async def get_today_plan(
    plan_repo=Depends(get_plan_repository)
):
    """Bugünün planını getir."""
    today = date.today()
    plan = plan_repo.get_by_date(today)
    
    if not plan:
        raise HTTPException(404, "Bugün için plan bulunamadı")
    
    return PlanResponse(
        id=plan.id or "",
        date=plan.date.isoformat(),
        mission=plan.mission,
        content=plan.content,
        tasks=[PlanTask(time=t.time, description=t.description, completed=t.completed) for t in plan.tasks],
        completion_rate=plan.get_completion_rate(),
        weather=plan.weather,
        active_course=plan.active_course
    )


@router.post("/generate", response_model=PlanResponse)
async def generate_plan(
    request: CreatePlanRequest,
    plan_service=Depends(get_plan_service)
):
    """Yeni plan oluştur."""
    plan = plan_service.generate_plan(
        user_note=request.user_note,
        active_course=request.active_course,
        weather=request.weather
    )
    
    return PlanResponse(
        id=plan.id or "",
        date=plan.date.isoformat(),
        mission=plan.mission,
        content=plan.content,
        tasks=[PlanTask(time=t.time, description=t.description, completed=t.completed) for t in plan.tasks],
        completion_rate=plan.get_completion_rate(),
        weather=plan.weather,
        active_course=plan.active_course
    )


@router.put("/{plan_date}", response_model=PlanResponse)
async def update_plan(
    plan_date: str,
    request: UpdatePlanRequest,
    plan_service=Depends(get_plan_service),
    plan_repo=Depends(get_plan_repository)
):
    """Planı güncelle."""
    try:
        target_date = date.fromisoformat(plan_date)
    except ValueError:
        raise HTTPException(400, "Geçersiz tarih formatı")
    
    plan = plan_repo.get_by_date(target_date)
    if not plan:
        raise HTTPException(404, "Plan bulunamadı")
    
    plan.content = request.content
    if request.mission:
        plan.mission = request.mission
    
    if not plan_service.update_plan(plan):
        raise HTTPException(500, "Plan güncellenemedi")
    
    return PlanResponse(
        id=plan.id or "",
        date=plan.date.isoformat(),
        mission=plan.mission,
        content=plan.content,
        tasks=[PlanTask(time=t.time, description=t.description, completed=t.completed) for t in plan.tasks],
        completion_rate=plan.get_completion_rate(),
        weather=plan.weather,
        active_course=plan.active_course
    )


@router.get("/{plan_date}", response_model=PlanResponse)
async def get_plan(
    plan_date: str,
    plan_repo=Depends(get_plan_repository)
):
    """Tarihe göre plan getir."""
    try:
        target_date = date.fromisoformat(plan_date)
    except ValueError:
        raise HTTPException(400, "Geçersiz tarih formatı")
    
    plan = plan_repo.get_by_date(target_date)
    if not plan:
        raise HTTPException(404, "Plan bulunamadı")
    
    return PlanResponse(
        id=plan.id or "",
        date=plan.date.isoformat(),
        mission=plan.mission,
        content=plan.content,
        tasks=[PlanTask(time=t.time, description=t.description, completed=t.completed) for t in plan.tasks],
        completion_rate=plan.get_completion_rate(),
        weather=plan.weather,
        active_course=plan.active_course
    )
