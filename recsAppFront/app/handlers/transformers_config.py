"""
PyTorch Device Configuration for Sentence Transformers

This module provides utilities for configuring PyTorch device usage
for CPU vs GPU (CUDA) operation.
"""

import os
import torch


def get_device() -> str:
    """
    Get the appropriate device for PyTorch operations.

    Priority:
    1. Explicit device setting via environment variable or config
    2. CUDA if available and not forced to CPU
    3. CPU as fallback

    Returns:
        str: 'cuda', 'cpu', or other device name
    """
    # Check for explicit device override
    force_device = os.getenv("PYTORCH_DEVICE")
    if force_device:
        return force_device

    # Check if CUDA is available
    if torch.cuda.is_available():
        # Check if we should prefer CPU even with CUDA available
        prefer_cpu = os.getenv("FORCE_CPU", "false").lower() == "true"
        if prefer_cpu:
            return "cpu"
        return "cuda"

    # Fallback to CPU
    return "cpu"


def get_torch_device():
    """
    Get the actual torch.device object.

    Returns:
        torch.device: PyTorch device object
    """
    device_name = get_device()
    return torch.device(device_name)


def print_device_info():
    """Print detailed device information for debugging."""
    print("=== PyTorch Device Information ===")

    # Check CUDA availability
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")

    if cuda_available:
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"Number of GPUs: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
            print(
                f"  Memory: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB"
            )

    # Get current device
    device = get_device()
    print(f"\nSelected Device: {device}")
    print(f"Device Object: {get_torch_device()}")

    # Show CPU info
    print(f"\nCPU Count: {torch.get_num_threads()}")
    print(f"PyTorch Version: {torch.__version__}")
    print("=" * 30)


def optimize_for_cpu():
    """
    Apply CPU-specific optimizations for better performance.
    """
    # Set number of threads for PyTorch CPU operations
    num_threads = os.getenv("PYTORCH_THREADS", str(os.cpu_count()))
    torch.set_num_threads(int(num_threads))

    # Optimize MKL for CPU (if available)
    if hasattr(torch, "backends") and hasattr(torch.backends, "mkldnn"):
        torch.backends.mkldnn.enabled = True
        torch.backends.mkldnn.flags = "SPEED"

    print(f"CPU Optimization: {num_threads} threads, MKL-DNN enabled")


def configure_device():
    """
    Configure the PyTorch device and apply optimizations.

    This should be called once at application startup.
    """
    device = get_device()
    print(f"Configuring PyTorch to use: {device}")

    if device == "cpu":
        optimize_for_cpu()
    else:
        # GPU-specific optimizations
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
        print(f"GPU Optimization: cuDNN benchmark enabled")

    return device


# Convenience functions
def is_cuda_available() -> bool:
    """Check if CUDA is available."""
    return torch.cuda.is_available()


def is_using_cuda() -> bool:
    """Check if current configuration is using CUDA."""
    return get_device() == "cuda"


def is_using_cpu() -> bool:
    """Check if current configuration is using CPU."""
    return get_device() == "cpu"
