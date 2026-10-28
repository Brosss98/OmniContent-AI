"""Content generation using LLMs (Ollama, OpenAI, Anthropic) with LangChain."""

from __future__ import annotations

import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.config import LLMProvider, Settings
from app.templates import get_template

logger = logging.getLogger(__name__)


class ConfigurationError(RuntimeError):
    """LLM configuration incomplete or invalid."""


# The content of templates is passed as a *variable*, not concatenated to the prompt:
# this way any curly braces in community templates don't break the formatting.
_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_prompt}"),
        (
            "human",
            "{instructions}\n\n"
            "Write the output in {language} language.\n"
            "Just give back the final content, no preamble.\n\n"
            "Source text:\n<<<\n{source_text}\n>>>",
        ),
    ]
)


def build_chat_model(
    settings: Settings,
    provider: LLMProvider | None = None,
    model: str | None = None,
) -> BaseChatModel:
    """Chat model factory. The imports are lazy: you only need the package of the provider you use."""

    provider = provider or settings.llm_provider
    model = model or settings.default_model_for(provider)
    temperature = settings.llm_temperature
    logger.info("LLM: provider=%s, model=%s", provider.value, model)

    match provider:

        case LLMProvider.OLLAMA:

            from langchain_ollama import ChatOllama

            return ChatOllama(model=model, base_url=settings.ollama_base_url, temperature=temperature)

        case LLMProvider.OPENAI:

            if settings.openai_api_key is None:

                raise ConfigurationError("OPENAI_API_KEY missing in the .env file")

            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=model, api_key=settings.openai_api_key, temperature=temperature)

        case LLMProvider.ANTHROPIC:

            if settings.anthropic_api_key is None:

                raise ConfigurationError("ANTHROPIC_API_KEY missing in the .env file")

            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model_name=model, api_key=settings.anthropic_api_key, 
                temperature=temperature, max_tokens=4096,
                timeout=None, stop=None
            )

    raise ConfigurationError(f"Provider not supported: {provider}")


class ContentGenerator:
    """Transform a source text into the requested target format."""

    def __init__(self, llm: BaseChatModel, output_language: str = "english") -> None:

        self._chain = _PROMPT | llm | StrOutputParser()
        self.output_language = output_language

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        provider: LLMProvider | None = None,
        model: str | None = None,
    ) -> ContentGenerator:

        return cls(build_chat_model(settings, provider, model), settings.output_language)

    def generate(self, source_text: str, target: str) -> str:
        """Generate the content for `target` (e.g., 'LinkedIn', 'Twitter', 'newsletter')."""

        if not source_text.strip():

            raise ValueError("The source text is empty.")

        template = get_template(target)

        return self._chain.invoke(
            {
                "system_prompt": template.system_prompt,
                "instructions": template.instructions,
                "language": self.output_language,
                "source_text": source_text,
            }
        ).strip()