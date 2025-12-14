"""
Profile API
~~~~~~~~~~~

Kullanıcı profili yönetimi.
"""

from pathlib import Path
from typing import Optional

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...core.config import get_settings

router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileResponse(BaseModel):
    """Profil yanıtı."""
    isim: str
    meslek: str
    ulke: str
    sehir: str
    gun_baslangici: str
    gun_bitisi: str
    egitim_programi: Optional[dict] = None
    hedefler: Optional[dict] = None
    yasak_kelimeler: list[str] = []


class ProfileUpdateRequest(BaseModel):
    """Profil güncelleme isteği."""
    isim: Optional[str] = None
    meslek: Optional[str] = None
    ulke: Optional[str] = None
    sehir: Optional[str] = None
    gun_baslangici: Optional[str] = None
    gun_bitisi: Optional[str] = None
    yasak_kelimeler: Optional[list[str]] = None


class CourseAddRequest(BaseModel):
    """Kurs ekleme isteği."""
    isim: str
    platform: str
    durum: str = "Aktif"


@router.get("/", response_model=ProfileResponse)
async def get_profile():
    """Kullanıcı profilini getir."""
    settings = get_settings()
    profile = settings.get_profile()
    
    if not profile:
        raise HTTPException(404, "Profil bulunamadı")
    
    return ProfileResponse(
        isim=profile.get("isim", "Kullanıcı"),
        meslek=profile.get("meslek", ""),
        ulke=profile.get("ulke", ""),
        sehir=profile.get("sehir", ""),
        gun_baslangici=profile.get("gun_baslangici", "09:00"),
        gun_bitisi=profile.get("gun_bitisi", "23:00"),
        egitim_programi=profile.get("egitim_programi"),
        hedefler=profile.get("hedefler"),
        yasak_kelimeler=profile.get("yasak_kelimeler", [])
    )


@router.put("/")
async def update_profile(request: ProfileUpdateRequest):
    """Profili güncelle."""
    settings = get_settings()
    profile_path = Path(settings.profile_path)
    
    # Mevcut profili oku
    profile = settings.get_profile()
    
    # Güncellemeleri uygula
    if request.isim is not None:
        profile["isim"] = request.isim
    if request.meslek is not None:
        profile["meslek"] = request.meslek
    if request.ulke is not None:
        profile["ulke"] = request.ulke
    if request.sehir is not None:
        profile["sehir"] = request.sehir
    if request.gun_baslangici is not None:
        profile["gun_baslangici"] = request.gun_baslangici
    if request.gun_bitisi is not None:
        profile["gun_bitisi"] = request.gun_bitisi
    if request.yasak_kelimeler is not None:
        profile["yasak_kelimeler"] = request.yasak_kelimeler
    
    # Kaydet
    try:
        with open(profile_path, "w", encoding="utf-8") as f:
            yaml.dump(profile, f, allow_unicode=True, default_flow_style=False)
        return {"success": True}
    except Exception as e:
        raise HTTPException(500, f"Profil kaydedilemedi: {str(e)}")


@router.get("/courses")
async def get_courses():
    """Eğitim programındaki kursları getir."""
    settings = get_settings()
    profile = settings.get_profile()
    
    courses = profile.get("egitim_programi", {}).get("durum", [])
    return {"courses": courses}


@router.post("/courses")
async def add_course(request: CourseAddRequest):
    """Yeni kurs ekle."""
    settings = get_settings()
    profile_path = Path(settings.profile_path)
    profile = settings.get_profile()
    
    # egitim_programi yoksa oluştur
    if "egitim_programi" not in profile:
        profile["egitim_programi"] = {"durum": []}
    if "durum" not in profile["egitim_programi"]:
        profile["egitim_programi"]["durum"] = []
    
    # Kurs ekle
    new_course = {
        "isim": request.isim,
        "platform": request.platform,
        "durum": request.durum
    }
    profile["egitim_programi"]["durum"].append(new_course)
    
    # Kaydet
    try:
        with open(profile_path, "w", encoding="utf-8") as f:
            yaml.dump(profile, f, allow_unicode=True, default_flow_style=False)
        return {"success": True, "course": new_course}
    except Exception as e:
        raise HTTPException(500, f"Kurs eklenemedi: {str(e)}")


@router.delete("/courses/{course_name}")
async def remove_course(course_name: str):
    """Kursu kaldır."""
    settings = get_settings()
    profile_path = Path(settings.profile_path)
    profile = settings.get_profile()
    
    courses = profile.get("egitim_programi", {}).get("durum", [])
    
    # Kursu bul ve kaldır
    new_courses = [c for c in courses if c.get("isim") != course_name]
    
    if len(new_courses) == len(courses):
        raise HTTPException(404, "Kurs bulunamadı")
    
    profile["egitim_programi"]["durum"] = new_courses
    
    # Kaydet
    try:
        with open(profile_path, "w", encoding="utf-8") as f:
            yaml.dump(profile, f, allow_unicode=True, default_flow_style=False)
        return {"success": True}
    except Exception as e:
        raise HTTPException(500, f"Kurs kaldırılamadı: {str(e)}")


@router.get("/banned-keywords")
async def get_banned_keywords():
    """Yasaklı kelimeleri getir."""
    settings = get_settings()
    profile = settings.get_profile()
    
    return {
        "keywords": profile.get("yasak_kelimeler", []),
        "default_keywords": settings.banned_keywords
    }


@router.put("/banned-keywords")
async def update_banned_keywords(keywords: list[str]):
    """Yasaklı kelimeleri güncelle."""
    settings = get_settings()
    profile_path = Path(settings.profile_path)
    profile = settings.get_profile()
    
    profile["yasak_kelimeler"] = keywords
    
    try:
        with open(profile_path, "w", encoding="utf-8") as f:
            yaml.dump(profile, f, allow_unicode=True, default_flow_style=False)
        return {"success": True, "keywords": keywords}
    except Exception as e:
        raise HTTPException(500, f"Yasaklı kelimeler kaydedilemedi: {str(e)}")




