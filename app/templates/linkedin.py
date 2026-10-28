from app.templates.base import ContentTemplate

TEMPLATE = ContentTemplate(
    key="linkedin",
    label="LinkedIn Post",
    system_prompt=(
        "You are an experienced LinkedIn ghostwriter. You write in an authoritative but human way, "
        "avoiding clichés, excessive hashtags, and unnecessary emojis."
    ),
    instructions=(
        "Turn the source text into a LinkedIn post:\n"
        "- Initial hook of no more than 2 lines that creates curiosity.\n"
        "- Body with 3-5 key insights, short and spaced paragraphs.\n"
        "- Closing with a question or call-to-action.\n"
        "- Maximum 3 relevant hashtags at the bottom.\n"
        "- Maximum length: 1300 characters."
    ),
)