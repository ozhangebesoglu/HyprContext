"""
HyprContext - Hafıza Sohbet Arayüzü
Geçmiş aktivitelere dayalı semantik arama ve sohbet.
"""

import logging

import ollama
from rich.console import Console

from config import MODEL_CHAT
from database import semantic_search

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
console = Console()


def ask_ai(question: str) -> str:
    """Hafızadan arama yapıp AI ile cevap üretir."""
    
    try:
        # Semantik arama
        results = semantic_search(question, n_results=10)
        
        if not results:
            return "Hafızada yeterli veri yok."
        
        # Bağlamı oluştur
        context_text = "\n".join([
            f"- [{r['time']}] {r['content']}" for r in results
        ])
        
        prompt = f"""Sen kişisel bir asistansın.
Kullanıcının geçmiş aktivitelerine erişimin var.

GEÇMİŞ KAYITLAR:
{context_text}

SORU: {question}

Sadece kayıtlara dayanarak Türkçe ve samimi cevap ver."""

        # Streaming yanıt
        stream = ollama.chat(
            model=MODEL_CHAT,
            messages=[{'role': 'user', 'content': prompt}],
            stream=True
        )
        
        full_response = ""
        for chunk in stream:
            part = chunk['message']['content']
            print(part, end="", flush=True)
            full_response += part
        
        return full_response
        
    except ConnectionError:
        logger.error("Ollama bağlantı hatası")
        return "❌ Ollama'ya bağlanılamadı. Servis çalışıyor mu?"
    except Exception as e:
        logger.error(f"Chat hatası: {e}")
        return f"❌ Bir hata oluştu: {e}"


def main():
    """Sohbet döngüsü."""
    console.print(f"[bold cyan]🤖 HyprContext Chat ({MODEL_CHAT})[/]")
    console.print("[dim]Çıkış için 'q' yaz[/]\n")
    
    while True:
        try:
            question = input("Soru: ").strip()
            
            if not question:
                continue
            
            if question.lower() == 'q':
                break
            
            print()
            ask_ai(question)
            print("\n")
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    console.print("\n[bold red]👋 Görüşürüz![/]")


if __name__ == "__main__":
    main()
