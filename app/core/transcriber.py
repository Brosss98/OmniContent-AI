"""Local audio/video transcription using faster-whisper."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from app.core.cuda_paths import register_nvidia_dlls

register_nvidia_dlls()

from faster_whisper import WhisperModel

from app.config import Settings

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[float], None]  # riceve un valore in [0.0, 1.0]

_CUDA_ERROR_MARKERS = ("cublas", "cudnn", "cuda")


def _is_cuda_runtime_error(exc: Exception) -> bool:

    msg = str(exc).lower()

    return any(marker in msg for marker in _CUDA_ERROR_MARKERS)


@dataclass(frozen=True, slots=True)
class Segment:

    start: float
    end: float
    text: str


@dataclass(frozen=True, slots=True)
class TranscriptionResult:

    text: str
    language: str
    language_probability: float
    duration: float
    segments: tuple[Segment, ...]


class Transcriber:
    """Wrapper for faster-whisper with lazy model loading."""

    def __init__(self, model_size: str = "small", device: str = "auto", compute_type: str = "int8") -> None:

        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model: WhisperModel | None = None

    @classmethod
    def from_settings(cls, settings: Settings) -> Transcriber:

        return cls(
            model_size=settings.whisper_model,
            device=settings.whisper_device.value,
            compute_type=settings.whisper_compute_type,
        )

    @property
    def model(self) -> WhisperModel:
        """The model (hundreds of MB) is loaded only on first use."""

        if self._model is None:

            logger.info("Loading Whisper '%s' (device=%s, compute=%s)",
                        self.model_size, self.device, self.compute_type)
            self._model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)

        return self._model

    def transcribe(
            self,
            audio_path: Path,
            language: str | None = None,
            on_progress: ProgressCallback | None = None,
    ) -> TranscriptionResult:
        """Transcribes an audio/video file. `language=None` enables auto-detect. If CUDA is not available, it falls back to the CPU."""

        if not audio_path.is_file():

            raise FileNotFoundError(f"File not found: {audio_path}")

        try:

            return self._run(audio_path, language, on_progress)

        except RuntimeError as exc:

            if self.device == "cpu" or not _is_cuda_runtime_error(exc):

                raise

            logger.warning(f"CUDA not available (%s): switching to CPU.", exc)
            self.device, self.compute_type, self._model = "cpu", "int8", None

            return self._run(audio_path, language, on_progress)

    def _run(
            self,
            audio_path: Path,
            language: str | None,
            on_progress: ProgressCallback | None,
    ) -> TranscriptionResult:

        segments_iter, info = self.model.transcribe(
            audio=str(audio_path),
            language=language,
            beam_size=5,
            vad_filter=True,  # skip the silences: faster and fewer hallucinations
        )

        logger.info("Lingua rilevata: %s (p=%.2f), durata %.0fs",
                    info.language, info.language_probability, info.duration)

        # The segments are a generator: the transcription happens during iteration.
        segments: list[Segment] = []

        for seg in segments_iter:

            segments.append(Segment(start=seg.start, end=seg.end, text=seg.text.strip()))

            if on_progress and info.duration:

                on_progress(min(seg.end / info.duration, 1.0))

        return TranscriptionResult(
            text=" ".join(s.text for s in segments if s.text),
            language=info.language,
            language_probability=info.language_probability,
            duration=info.duration,
            segments=tuple(segments),
        )