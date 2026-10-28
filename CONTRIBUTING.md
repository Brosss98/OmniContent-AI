# Contributing to OmniContent AI

Thanks for your interest! Contributions of any size are welcome.

## Development setup

```bash
git clone https://github.com/Brosss98/omnicontent-ai.git
cd omnicontent-ai
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pytest
```

## Adding a new output format (the easiest first contribution)

1. Create `app/templates/<name>.py` exposing a `TEMPLATE = ContentTemplate(...)` object
   (copy `linkedin.py` as a starting point).
2. Register it in the tuple inside `app/templates/__init__.py`.
3. Check it appears in `python main.py list-targets` and try it on a short text file.

`key` must be lowercase (`a-z`, `0-9`, `_`, `-`). Curly braces in prompts are safe:
template text is passed to LangChain as a variable, not as part of the prompt template.

## Pull request guidelines

- One feature or fix per PR, with a clear description of *why*.
- Type hints on all public functions; keep the core (`app/core`) independent of CLI/UI.
- Do not add a new dependency unless it is really needed; explain it in the PR.
- Never commit `.env`, API keys, audio/video files or generated output.
- Run `pytest` before opening the PR.

## Reporting bugs

Open an issue including: OS, Python version (`python --version`), the command you ran,
the full traceback and, if relevant, the output of `pip show faster-whisper av ctranslate2`.

By contributing, you agree that your contributions are licensed under the Apache License 2.0.
