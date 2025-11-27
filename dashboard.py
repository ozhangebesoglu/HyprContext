"""
HyprContext - Terminal Dashboard
Rich kütüphanesiyle canlı güncellenen terminal arayüzü.
"""

import json
import re
import time
import logging
from collections import deque
from datetime import datetime

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text

from config import HISTORY_FILE, MAX_DASHBOARD_ROWS

logging.basicConfig(level=logging.WARNING)
console = Console()


def read_last_entries(n: int) -> list[dict]:
    """Dosyanın son n satırını verimli bir şekilde okur."""
    if not HISTORY_FILE.exists():
        return []
    
    entries = []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            lines = deque(f, maxlen=n)
            for line in lines:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        logging.error(f"Dosya okuma hatası: {e}")
        return []
    
    # En yeniden en eskiye sırala
    return list(reversed(entries))


def extract_tags(text: str) -> str:
    """Metinden etiketleri ayıklar."""
    # Metnin sonundaki [Etiket1, Etiket2] kısmını bul
    match = re.search(r'\[([^\]]+)\]$', text.strip())
    
    if match:
        tags_content = match.group(1)
        # Virgülleri şık ayraçlarla değiştir
        formatted_tags = tags_content.replace(",", "  [dim white]•[/] ")
        return f"[bold yellow]{formatted_tags}[/]"
    
    # Etiket bulunamazsa metnin başını göster
    return f"[dim white]{text[:60]}...[/]"


def generate_table() -> Table:
    """Rich tablosunu oluşturur."""
    table = Table(
        expand=True,
        box=None,
        padding=(0, 2),
        collapse_padding=True
    )
    
    table.add_column("Saat", justify="right", style="bold green", width=10)
    table.add_column("Tespit Edilen Konular", style="bold cyan", ratio=1)

    data = read_last_entries(MAX_DASHBOARD_ROWS)
    
    if not data:
        table.add_row("---", "[italic grey50]Veri bekleniyor...[/]")
    else:
        for entry in data:
            try:
                dt = datetime.fromisoformat(entry["timestamp"])
                time_str = dt.strftime("%H:%M:%S")
                summary = entry["summary"]
                display_text = extract_tags(summary)
                table.add_row(time_str, display_text)
            except (KeyError, ValueError):
                continue

    return table


def main():
    """Canlı dashboard döngüsü."""
    header = Panel(
        Text("🚀 HyprContext Canlı Akışı", justify="center", style="bold magenta"),
        style="cyan",
        subtitle=f"[dim]Son {MAX_DASHBOARD_ROWS} Kayıt[/]"
    )

    with Live(console=console, refresh_per_second=1) as live:
        while True:
            table = generate_table()
            
            layout = Layout()
            layout.split_column(
                Layout(header, size=3),
                Layout(table)
            )
            
            live.update(layout)
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]👋 Dashboard kapatıldı.[/]")
