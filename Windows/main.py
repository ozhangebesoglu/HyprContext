"""
HyprContext Windows - Ana Uygulama
Ekran aktivitelerini izler, analiz eder ve kaydeder.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import get_config, Config
from window import get_window_context, get_active_window_string, check_any_distraction
from capture import take_screenshot_base64, cleanup_screenshot
from analyzer import OllamaAnalyzer, AnalysisResult
from database import Database, get_database
from focus import FocusTracker, get_focus_tracker
from notifier import (
    send_startup_notification,
    send_focus_warning,
    send_time_warning,
    send_limit_warning,
    handle_focus_warning
)

# CLI uygulaması
app = typer.Typer(
    name="hyprcontext",
    help="🧠 HyprContext - Windows Aktivite İzleyici",
    add_completion=False
)

console = Console()


def setup_logging(verbose: bool = False):
    """Logging ayarları"""
    logger.remove()
    
    level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level=level,
        colorize=True
    )
    
    # Dosyaya da yaz
    logger.add(
        "hyprcontext.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="DEBUG",
        rotation="1 day",
        retention="7 days"
    )


async def process_capture(
    config: Config,
    db: Database,
    analyzer: OllamaAnalyzer,
    focus_tracker: FocusTracker
) -> Optional[str]:
    """Ekran görüntüsü al ve analiz et"""
    
    # 1. Dikkat dağıtıcı kontrolü
    distraction = check_any_distraction(config.banned_list)
    if distraction:
        warning = focus_tracker.add_distraction(config.capture_interval, distraction)
        if warning:
            handle_focus_warning(warning)
        logger.warning(f"⚠️ Dikkat dağıtıcı: {distraction}")
    
    # 2. Pencere bağlamı al
    context = get_window_context(config.banned_list)
    logger.debug(f"Bağlam: {context}")
    
    # 3. Screenshot al
    image_b64 = take_screenshot_base64()
    if not image_b64:
        logger.error("Screenshot alınamadı")
        return None
    
    # 4. Kısa süreli bellek
    history = db.get_short_term_memory(config.ram_size)
    
    # 5. AI Analizi
    start_time = time.time()
    
    result = analyzer.analyze_image(
        image_base64=image_b64,
        active_window=f"{context.app_name} | {context.window_title}",
        background_apps=", ".join(context.background_apps) if context.background_apps else "Yok",
        detected_language=context.detected_language,
        detected_file=context.detected_file,
        history=history
    )
    
    elapsed = time.time() - start_time
    logger.info(f"Analiz tamamlandı ({elapsed:.2f}s)")
    
    # 6. Veritabanına kaydet
    tags = ", ".join(result.tags)
    db.save(result.summary, tags)
    
    # 7. Kısa süreli belleği güncelle
    db.add_to_short_term_memory(result.summary[:100])
    db.cleanup_old_memory(config.ram_size)
    
    logger.info(f"📝 {result.summary}")
    
    return result.summary


async def run_daemon(config: Config):
    """Ana izleme döngüsü"""
    logger.info("🚀 HyprContext Windows başlatıldı")
    logger.info(f"📊 Capture interval: {config.capture_interval}s")
    logger.info(f"🔍 Model: {config.model_vision}")
    logger.info(f"🚫 Yasaklı: {config.banned_list}")
    
    # Bileşenleri başlat
    db = get_database(config.database_path)
    analyzer = OllamaAnalyzer(config.ollama_url, config.model_vision)
    focus_tracker = get_focus_tracker(
        Path("focus_data.json"),
        config.daily_distraction_limit,
        config.distraction_threshold
    )
    
    # Başlangıç bildirimi
    send_startup_notification()
    
    try:
        while True:
            try:
                await process_capture(config, db, analyzer, focus_tracker)
            except Exception as e:
                logger.error(f"İşlem hatası: {e}")
            
            await asyncio.sleep(config.capture_interval)
            
    except asyncio.CancelledError:
        logger.info("Daemon durduruldu")
    finally:
        analyzer.close()
        db.close()


@app.command()
def run(
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Ayrıntılı çıktı"),
    interval: Optional[int] = typer.Option(None, "-i", "--interval", help="Yakalama aralığı (saniye)")
):
    """
    🚀 Aktivite izlemeyi başlat
    """
    setup_logging(verbose)
    config = get_config()
    
    if interval:
        config.capture_interval = interval
    
    try:
        asyncio.run(run_daemon(config))
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️  Durduruldu[/yellow]")


@app.command()
def recent(
    count: int = typer.Option(10, "-n", "--count", help="Gösterilecek kayıt sayısı"),
    today: bool = typer.Option(False, "-t", "--today", help="Sadece bugün")
):
    """
    📋 Son aktiviteleri göster
    """
    config = get_config()
    db = get_database(config.database_path)
    
    if today:
        records = db.get_today()[:count]
        title = "Bugünün Aktiviteleri"
    else:
        records = db.get_recent(count)
        title = f"Son {count} Aktivite"
    
    if not records:
        console.print("[yellow]Henüz kayıt yok.[/yellow]")
        return
    
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Zaman", style="dim", width=8)
    table.add_column("Aktivite", style="white")
    table.add_column("Etiketler", style="green")
    
    for record in records:
        time_str = record.timestamp.strftime("%H:%M")
        summary = record.summary[:60] + "..." if len(record.summary) > 60 else record.summary
        table.add_row(time_str, summary, record.tags)
    
    console.print(table)


@app.command()
def search(
    query: str = typer.Argument(..., help="Aranacak metin"),
    limit: int = typer.Option(20, "-n", "--limit", help="Maksimum sonuç")
):
    """
    🔍 Aktivitelerde ara
    """
    config = get_config()
    db = get_database(config.database_path)
    
    records = db.search(query, limit)
    
    if not records:
        console.print(f"[yellow]'{query}' için sonuç bulunamadı.[/yellow]")
        return
    
    table = Table(title=f"'{query}' araması", show_header=True, header_style="bold cyan")
    table.add_column("Tarih", style="dim", width=12)
    table.add_column("Aktivite", style="white")
    table.add_column("Etiketler", style="green")
    
    for record in records:
        date_str = record.timestamp.strftime("%m-%d %H:%M")
        summary = record.summary[:55] + "..." if len(record.summary) > 55 else record.summary
        table.add_row(date_str, summary, record.tags)
    
    console.print(table)


@app.command()
def stats():
    """
    📊 İstatistikleri göster
    """
    config = get_config()
    db = get_database(config.database_path)
    focus_tracker = get_focus_tracker(
        Path("focus_data.json"),
        config.daily_distraction_limit,
        config.distraction_threshold
    )
    
    db_stats = db.get_stats()
    focus_stats = focus_tracker.get_stats()
    
    # Veritabanı istatistikleri
    panel1 = Panel(
        f"""[bold]Toplam Kayıt:[/bold] {db_stats['total']}
[bold]Bugün:[/bold] {db_stats['today']}
[bold]Son 7 Gün:[/bold] {db_stats['week']}""",
        title="📊 Veritabanı",
        border_style="cyan"
    )
    
    # Odak istatistikleri
    status = "🔴 Limit Doldu" if focus_stats['limit_reached'] else "🟢 Normal"
    panel2 = Panel(
        f"""[bold]Durum:[/bold] {status}
[bold]Kullanılan:[/bold] {focus_stats['used_formatted']} (%{focus_stats['percentage']})
[bold]Kalan:[/bold] {focus_stats['remaining_formatted']}
[bold]Dikkat Dağıtıcı:[/bold] {focus_stats['distraction_count']} kez""",
        title="🎯 Odak Takibi",
        border_style="green"
    )
    
    console.print(panel1)
    console.print(panel2)
    
    # En sık etiketler
    if db_stats['top_tags']:
        console.print("\n[bold cyan]🏷️  En Sık Etiketler:[/bold cyan]")
        for tag, count in db_stats['top_tags'][:5]:
            console.print(f"  • {tag}: {count}")


@app.command()
def capture():
    """
    📸 Tek seferlik ekran yakala ve analiz et
    """
    setup_logging(verbose=True)
    config = get_config()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analiz ediliyor...", total=None)
        
        db = get_database(config.database_path)
        analyzer = OllamaAnalyzer(config.ollama_url, config.model_vision)
        focus_tracker = get_focus_tracker(
            Path("focus_data.json"),
            config.daily_distraction_limit,
            config.distraction_threshold
        )
        
        async def do_capture():
            return await process_capture(config, db, analyzer, focus_tracker)
        
        result = asyncio.run(do_capture())
        
        analyzer.close()
        
    if result:
        console.print(Panel(result, title="📝 Analiz Sonucu", border_style="green"))
    else:
        console.print("[red]Analiz başarısız[/red]")


@app.command()
def focus():
    """
    🎯 Odak oturumu başlat
    """
    config = get_config()
    focus_tracker = get_focus_tracker(
        Path("focus_data.json"),
        config.daily_distraction_limit,
        config.distraction_threshold
    )
    
    focus_tracker.start_focus_session()
    stats = focus_tracker.get_stats()
    
    console.print(Panel(
        f"""[bold green]✓ Odak oturumu #{stats['focus_sessions']} başladı![/bold green]

Dikkat dağıtıcı sayacı sıfırlandı.
Kalan süre: {stats['remaining_formatted']}""",
        title="🎯 Odak Modu",
        border_style="green"
    ))


@app.command()
def version():
    """
    ℹ️  Versiyon bilgisi
    """
    console.print(Panel(
        """[bold cyan]HyprContext Windows[/bold cyan]
Version: 1.0.0
Python: {}.{}.{}

🧠 Yapay zeka destekli aktivite izleyici""".format(*sys.version_info[:3]),
        title="ℹ️  Hakkında",
        border_style="blue"
    ))


if __name__ == "__main__":
    app()



