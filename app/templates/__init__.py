"""Template registry. To add a format: create the module and register it here."""

from app.templates import linkedin, newsletter, twitter
from app.templates.base import ContentTemplate

TEMPLATES: dict[str, ContentTemplate] = {
    t.key: t for t in (linkedin.TEMPLATE, newsletter.TEMPLATE, twitter.TEMPLATE)
}


def available_targets() -> list[str]:
    
    return sorted(TEMPLATES)


def get_template(key: str) -> ContentTemplate:

    try:

        return TEMPLATES[key.lower()]

    except KeyError as exc:

        raise ValueError(
            f"Target '{key}' not supported. Available: {','.join(available_targets())}"
        ) from exc