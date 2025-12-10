"""
System Monitor Service
~~~~~~~~~~~~~~~~~~~~~~

CPU, RAM, GPU, Disk sistem kaynaklarını izler.
"""

import logging
from dataclasses import dataclass, asdict
from typing import Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SystemStats:
    """Sistem istatistikleri."""
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    gpu_percent: Optional[float] = None
    gpu_memory_percent: Optional[float] = None
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    
    def to_dict(self) -> dict:
        return asdict(self)


class SystemMonitorService:
    """Sistem kaynak izleme servisi."""
    
    def __init__(self):
        self._last_net_io = None
        
    def get_stats(self) -> Optional[SystemStats]:
        """Anlık sistem istatistiklerini al."""
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil kurulu değil")
            return None
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # RAM
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024 ** 3)
            memory_total_gb = memory.total / (1024 ** 3)
            
            # Disk
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024 ** 3)
            disk_total_gb = disk.total / (1024 ** 3)
            
            # Network
            net_io = psutil.net_io_counters()
            network_sent_mb = net_io.bytes_sent / (1024 ** 2)
            network_recv_mb = net_io.bytes_recv / (1024 ** 2)
            
            # GPU (opsiyonel - NVIDIA)
            gpu_percent, gpu_memory_percent = self._get_gpu_stats()
            
            return SystemStats(
                cpu_percent=round(cpu_percent, 1),
                memory_percent=round(memory_percent, 1),
                memory_used_gb=round(memory_used_gb, 2),
                memory_total_gb=round(memory_total_gb, 2),
                disk_percent=round(disk_percent, 1),
                disk_used_gb=round(disk_used_gb, 2),
                disk_total_gb=round(disk_total_gb, 2),
                gpu_percent=gpu_percent,
                gpu_memory_percent=gpu_memory_percent,
                network_sent_mb=round(network_sent_mb, 2),
                network_recv_mb=round(network_recv_mb, 2)
            )
            
        except Exception as e:
            logger.error(f"Sistem istatistikleri alınamadı: {e}")
            return None
    
    def _get_gpu_stats(self) -> tuple[Optional[float], Optional[float]]:
        """GPU istatistiklerini al (NVIDIA veya AMD)."""
        # NVIDIA GPU (nvidia-smi)
        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total", 
                 "--format=csv,nounits,noheader"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                parts = result.stdout.strip().split(", ")
                if len(parts) >= 3:
                    gpu_util = float(parts[0])
                    mem_used = float(parts[1])
                    mem_total = float(parts[2])
                    gpu_mem_percent = (mem_used / mem_total) * 100 if mem_total > 0 else 0
                    return round(gpu_util, 1), round(gpu_mem_percent, 1)
        except Exception:
            pass
        
        # AMD GPU (rocm-smi) - fallback
        try:
            import subprocess
            result = subprocess.run(
                ["rocm-smi", "--showuse", "--csv"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:
                    # Basit parsing
                    for line in lines[1:]:
                        if "GPU" in line.upper():
                            parts = line.split(",")
                            if len(parts) > 1:
                                try:
                                    gpu_util = float(parts[1].strip().replace("%", ""))
                                    return round(gpu_util, 1), None
                                except ValueError:
                                    pass
        except Exception:
            pass
        
        return None, None
    
    def is_available(self) -> bool:
        """Servis kullanılabilir mi?"""
        return PSUTIL_AVAILABLE
