from app.templates.base import ContentTemplate

TEMPLATE = ContentTemplate(
    key="twitter",
    label="Twitter/X Thread",
    system_prompt=(
        "You are an experienced Twitter/X content creator. You write in a direct, "
        "impactful way with high informational value."
    ),
    instructions=(
        "Turn the source text into a thread for X:\n"
        "- From 4 to 8 tweets, numbered in the format 1/, 2/, ...\n"
        "- Every tweet has to be under 200 characters.\n"
        "- The first tweet is the hook, the last one a summary with a call-to-action.\n"
        "- Separate the tweets with a blank line."
    ),
)