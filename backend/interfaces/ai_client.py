"""
AI Client Interface
~~~~~~~~~~~~~~~~~~~

AI modelleri için soyut temel sınıf.
Open/Closed Principle: Yeni model eklemek için bu interface'i implement et.
"""

from abc import ABC, abstractmethod
from typing import Optional, Iterator, Union


class IAIClient(ABC):
    """AI modeli için soyut interface."""
    
    @abstractmethod
    def generate(self, prompt: str, image: Optional[bytes] = None) -> str:
        """Prompt'a göre yanıt üret.
        
        Args:
            prompt: AI'a gönderilecek metin
            image: Opsiyonel görüntü (base64 encoded)
            
        Returns:
            AI'ın ürettiği yanıt
        """
        pass
    
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Metin için embedding vektörü oluştur.
        
        Args:
            text: Embedding oluşturulacak metin
            
        Returns:
            Embedding vektörü
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Kullanılan model adını döndür."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Modelin kullanılabilir olup olmadığını kontrol et."""
        pass
    
    @abstractmethod
    def chat(
        self, 
        messages: list[dict], 
        stream: bool = False
    ) -> Union[str, Iterator[str]]:
        """Chat completion (streaming destekli).
        
        Args:
            messages: Mesaj listesi [{"role": "user", "content": "..."}]
            stream: Streaming açık mı
            
        Returns:
            Yanıt (streaming ise Iterator, değilse str)
        """
        pass
