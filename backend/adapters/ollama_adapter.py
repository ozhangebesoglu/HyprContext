"""
Ollama Adapter
~~~~~~~~~~~~~~

Ollama AI client implementasyonu.
Open/Closed: Yeni AI provider için yeni adapter oluştur.
"""

import logging
from typing import Optional

import ollama

from ..interfaces.ai_client import IAIClient

logger = logging.getLogger(__name__)


class OllamaAdapter(IAIClient):
    """Ollama AI client implementasyonu."""
    
    def __init__(
        self,
        model_name: str = "gemma3",
        embed_model: str = "mxbai-embed-large",
        base_url: str = "http://localhost:11434"
    ):
        """
        Args:
            model_name: Kullanılacak model adı
            embed_model: Embedding modeli adı
            base_url: Ollama API URL'i
        """
        self.model_name = model_name
        self.embed_model = embed_model
        self.base_url = base_url
    
    def generate(self, prompt: str, image: Optional[bytes] = None) -> str:
        """Prompt'a göre yanıt üret.
        
        Args:
            prompt: AI'a gönderilecek metin
            image: Opsiyonel görüntü (base64 encoded)
            
        Returns:
            AI'ın ürettiği yanıt
        """
        try:
            kwargs = {
                "model": self.model_name,
                "prompt": prompt,
            }
            
            if image:
                # Base64 bytes'ı string'e çevir
                image_str = image.decode('utf-8') if isinstance(image, bytes) else image
                kwargs["images"] = [image_str]
            
            response = ollama.generate(**kwargs)
            return response.get("response", "")
            
        except Exception as e:
            logger.error(f"Ollama generate hatası: {e}")
            raise
    
    def embed(self, text: str) -> list[float]:
        """Metin için embedding vektörü oluştur.
        
        Args:
            text: Embedding oluşturulacak metin
            
        Returns:
            Embedding vektörü
        """
        try:
            response = ollama.embeddings(
                model=self.embed_model,
                prompt=text
            )
            return response.get("embedding", [])
            
        except Exception as e:
            logger.error(f"Ollama embed hatası: {e}")
            raise
    
    def get_model_name(self) -> str:
        """Kullanılan model adını döndür."""
        return self.model_name
    
    def is_available(self) -> bool:
        """Modelin kullanılabilir olup olmadığını kontrol et."""
        try:
            models = ollama.list()
            model_names = [m.get("name", "") for m in models.get("models", [])]
            return self.model_name in model_names or f"{self.model_name}:latest" in model_names
        except Exception:
            return False
    
    def chat(self, messages: list[dict], stream: bool = False):
        """Chat completion (streaming destekli).
        
        Args:
            messages: Mesaj listesi [{"role": "user", "content": "..."}]
            stream: Streaming açık mı
            
        Yields/Returns:
            Yanıt (streaming ise parçalar, değilse tam yanıt)
        """
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                stream=stream
            )
            
            if stream:
                for chunk in response:
                    yield chunk.get("message", {}).get("content", "")
            else:
                return response.get("message", {}).get("content", "")
                
        except Exception as e:
            logger.error(f"Ollama chat hatası: {e}")
            raise
