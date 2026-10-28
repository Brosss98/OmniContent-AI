from app.templates.base import ContentTemplate

TEMPLATE = ContentTemplate(
    key="newsletter",
    label="Newsletter",
    system_prompt=(
        "You are the editor of a technical newsletter followed by professionals. "
        "Write in a clear, structured, and engaging way."
    ),
    instructions=(
        "Turn the source text into a newsletter number in Markdown:\n"
        "- Suggest an email subject (line 'Subject: ...').\n"
        "- Introduction of 2-3 sentences.\n"
        "- Sections with H2 titles for each main topic.\n"
        "- A final 'Key takeaways' box with 3 bullet points.\n"
        "- Warm regards."
    ),
)