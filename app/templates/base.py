"""Data model shared by all output templates."""

from pydantic import BaseModel, ConfigDict, Field


class ContentTemplate(BaseModel):
    """Declarative definition of a destination format."""

    model_config = ConfigDict(frozen=True)

    key: str = Field(pattern=r"^[a-z0-9_-]+$", description="Identifier used in CLI/UI")
    label: str
    system_prompt: str = Field(min_length=20)
    instructions: str = Field(min_length=20)