"""Centralized configuration of OmniContent AI, read from environment variables and configuration files."""
from __future__ import annotations

from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class WhisperDevice(str, Enum):
    """Supported devices for Whisper inference."""

    AUTO = "auto"
    CPU = "cpu"
    CUDA = "cuda"

class Settings(BaseSettings):
    """Application settings. Each field can be overridden by an env var with the same name."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,  # OPENAI_API_KEY= (vuota) viene trattata come None
        extra="ignore",
        case_sensitive=False,
    )

    # --- LLM ---
    llm_provider: LLMProvider = LLMProvider.OLLAMA
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4o-mini"

    anthropic_api_key: SecretStr | None = None
    anthropic_model: str = "claude-3-5-haiku-latest"

    # --- Whisper ---
    whisper_model: str = "small"
    whisper_device: WhisperDevice = WhisperDevice.AUTO
    whisper_compute_type: str = "int8"

    # --- Output ---
    output_dir: Path = Path("output")
    output_language: str = "english"
    log_level: str = "INFO"

    def default_model_for(self, provider: LLMProvider) -> str:
        """Returns the default model set up for the specified provider."""
        return {
            LLMProvider.OLLAMA: self.ollama_model,
            LLMProvider.OPENAI: self.openai_model,
            LLMProvider.ANTHROPIC: self.anthropic_model,
        }[provider]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    "Settings singleton: the .env is read only once."
    return Settings()