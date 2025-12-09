"""
Chat API
~~~~~~~~

AI sohbet endpointleri.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ...core.dependencies import get_ai_client, get_activity_repository

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Sohbet mesajı."""
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    """Sohbet isteği."""
    message: str
    context: Optional[str] = None  # Opsiyonel bağlam
    include_memory: bool = True  # Semantik arama dahil mi


class ChatResponse(BaseModel):
    """Sohbet yanıtı."""
    response: str
    context_used: list[str] = []  # Kullanılan bağlam (semantik aramadan)


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    ai_client=Depends(get_ai_client),
    activity_repo=Depends(get_activity_repository)
):
    """AI ile sohbet et."""
    context_parts = []
    context_used = []
    
    # Semantik arama ile bağlam ekle
    if request.include_memory:
        try:
            search_results = activity_repo.search(request.message, limit=5)
            if search_results:
                context_parts.append("İlgili geçmiş aktiviteler:")
                for act in search_results:
                    context_parts.append(f"- [{act.get_date()}] {act.summary}")
                    context_used.append(act.summary)
        except Exception:
            pass  # Arama başarısız olsa bile devam et
    
    # Manuel bağlam ekle
    if request.context:
        context_parts.append(f"\nEk Bağlam:\n{request.context}")
    
    # Prompt oluştur
    full_context = "\n".join(context_parts) if context_parts else ""
    
    prompt = f"""Sen HyprContext asistanısın. Kullanıcının aktivitelerini takip ediyorsun.
    
{full_context}

Kullanıcı: {request.message}

Yardımcı ve samimi bir şekilde yanıtla. Türkçe konuş."""
    
    try:
        response = ai_client.generate(prompt)
        
        return ChatResponse(
            response=response,
            context_used=context_used
        )
        
    except Exception as e:
        raise HTTPException(500, f"AI yanıt hatası: {str(e)}")


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    ai_client=Depends(get_ai_client),
    activity_repo=Depends(get_activity_repository)
):
    """AI ile streaming sohbet et."""
    context_parts = []
    
    # Semantik arama ile bağlam ekle
    if request.include_memory:
        try:
            search_results = activity_repo.search(request.message, limit=5)
            if search_results:
                context_parts.append("İlgili geçmiş aktiviteler:")
                for act in search_results:
                    context_parts.append(f"- [{act.get_date()}] {act.summary}")
        except Exception:
            pass
    
    # Manuel bağlam ekle
    if request.context:
        context_parts.append(f"\nEk Bağlam:\n{request.context}")
    
    full_context = "\n".join(context_parts) if context_parts else ""
    
    messages = [
        {
            "role": "system",
            "content": f"""Sen HyprContext asistanısın. Kullanıcının aktivitelerini takip ediyorsun.
            
{full_context}

Yardımcı ve samimi bir şekilde yanıtla. Türkçe konuş."""
        },
        {
            "role": "user",
            "content": request.message
        }
    ]
    
    async def generate():
        try:
            for chunk in ai_client.chat(messages, stream=True):
                yield chunk
        except Exception as e:
            yield f"[Hata: {str(e)}]"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )
