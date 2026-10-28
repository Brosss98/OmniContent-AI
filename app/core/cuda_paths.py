"""Makes the CUDA DLLs installed via nvidia-* pip packages visible on Windows."""

import os
import sys
from pathlib import Path


def register_nvidia_dlls() -> None:

    if sys.platform != "win32":

        return

    try:

        import nvidia  # namespace package created by nvidia-cublas-cu12 / nvidia-cudnn-cu12

    except ImportError:

        return

    for root in map(Path, nvidia.__path__):

        for bin_dir in root.glob("*/bin"):

            os.add_dll_directory(str(bin_dir))
            os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ['PATH']}"
