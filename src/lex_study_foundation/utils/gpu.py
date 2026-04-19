"""GPU detection utilities.

Designed to be import-safe even when torch is not installed.
Phase 1 does not require torch — this module gracefully degrades.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GpuInfo:
    """Snapshot of GPU state. All fields are strings for display."""

    available: bool
    name: str = "N/A"
    vram_total_gb: str = "N/A"
    vram_free_gb: str = "N/A"
    compute_capability: str = "N/A"
    cuda_version: str = "N/A"
    torch_version: str = "N/A"
    bf16_supported: str = "N/A"


def detect_gpu() -> GpuInfo:
    """Detect GPU capabilities. Returns a populated GpuInfo even if torch is absent."""
    try:
        import torch
    except ImportError:
        return GpuInfo(
            available=False,
            name="torch not installed",
            torch_version="not installed",
        )

    if not torch.cuda.is_available():
        return GpuInfo(
            available=False,
            name="no CUDA GPU detected",
            torch_version=torch.__version__,
            cuda_version=str(torch.version.cuda) if torch.version.cuda else "N/A",
        )

    props = torch.cuda.get_device_properties(0)
    total_gb = props.total_memory / (1024**3)

    try:
        allocated = torch.cuda.memory_allocated(0) / (1024**3)
        free_gb = total_gb - allocated
    except Exception:
        free_gb = -1.0

    return GpuInfo(
        available=True,
        name=torch.cuda.get_device_name(0),
        vram_total_gb=f"{total_gb:.1f}",
        vram_free_gb=f"{free_gb:.1f}" if free_gb >= 0 else "N/A",
        compute_capability=f"SM {props.major}.{props.minor}",
        cuda_version=str(torch.version.cuda) if torch.version.cuda else "N/A",
        torch_version=torch.__version__,
        bf16_supported=str(torch.cuda.is_bf16_supported()),
    )
