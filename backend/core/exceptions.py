"""
Exceptions
~~~~~~~~~~

Özel exception sınıfları ve error handler'ları.
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    """Standart hata yanıtı."""
    error: str
    message: str
    details: Optional[dict] = None


class HyprContextException(Exception):
    """Base exception sınıfı."""
    
    def __init__(
        self, 
        error: str, 
        message: str, 
        status_code: int = 500,
        details: Optional[dict] = None
    ):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class AIServiceException(HyprContextException):
    """AI servisi hataları."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            error="AI_SERVICE_ERROR",
            message=message,
            status_code=503,
            details=details
        )


class DatabaseException(HyprContextException):
    """Veritabanı hataları."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            error="DATABASE_ERROR",
            message=message,
            status_code=500,
            details=details
        )


class ValidationException(HyprContextException):
    """Doğrulama hataları."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            error="VALIDATION_ERROR",
            message=message,
            status_code=400,
            details=details
        )


class NotFoundException(HyprContextException):
    """Kayıt bulunamadı hatası."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            error="NOT_FOUND",
            message=f"{resource} bulunamadı: {identifier}",
            status_code=404,
            details={"resource": resource, "identifier": identifier}
        )


class ServiceUnavailableException(HyprContextException):
    """Servis kullanılamıyor hatası."""
    
    def __init__(self, service: str, message: Optional[str] = None):
        super().__init__(
            error="SERVICE_UNAVAILABLE",
            message=message or f"{service} servisi kullanılamıyor",
            status_code=503,
            details={"service": service}
        )


async def hyprcontext_exception_handler(
    request: Request, 
    exc: HyprContextException
) -> JSONResponse:
    """HyprContext exception handler."""
    logger.error(f"{exc.error}: {exc.message}", extra={"details": exc.details})
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.error,
            message=exc.message,
            details=exc.details
        ).model_dump()
    )


async def generic_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """Genel exception handler."""
    logger.exception(f"Beklenmeyen hata: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="Beklenmeyen bir hata oluştu",
            details={"type": type(exc).__name__}
        ).model_dump()
    )
