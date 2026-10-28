"""OmniContent AI command-line interface."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
from rich.table import Table

from app.config import LLMProvider, get_settings
from app.core.generator import ConfigurationError, ContentGenerator
from app.core.transcriber import Transcriber
from app.templates import TEMPLATES, available_targets

app = typer.Typer(
    name="omnicontent",
    help="OmniContent AI: from audio/video/text to content for social media, blogs, and newsletters.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

TEXT_EXTENSIONS = {".txt", ".md"}


def _setup_logging(level: str) -> None:

    logging.basicConfig(
        level=level.upper(), format="%(message)s",
        handlers=[RichHandler(console=console, show_path=False)],
    )


def _validate_target(value: str) -> str:
    
    if value.lower() not in TEMPLATES:

        raise typer.BadParameter(f"Allowed values: {', '.join(available_targets())}")

    return value.lower()


def _transcribe(transcriber: Transcriber, path: Path, language: str | None) -> str:

    with Progress(
        TextColumn("[bold blue]Transcription"), BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"), TimeElapsedColumn(), console=console
    ) as progress:

        task = progress.add_task("transcribe", total=1.0)

        result = transcriber.transcribe(
            path, language=language,
            on_progress=lambda p: progress.update(task, completed=p),
        )

        progress.update(task, completed=1.0)

        return result.text


@app.command("transcribe-and-generate")
def transcribe_and_generate(
    input_path: Annotated[Path, typer.Option(
        "--input", "-i", exists=True, dir_okay=False, readable=True, resolve_path=True,
        help="Audio/video file or text (.txt/.md).",
    )],
    target: Annotated[str, typer.Option(
        "--target", "-t", callback=_validate_target, help="Destination format.",
    )] = "linkedin",
    output: Annotated[Optional[Path], typer.Option(
        "--output", "-o", help="Output file (default: OUTPUT_DIR/<name>_<target>.md).",
    )] = None,
    provider: Annotated[Optional[LLMProvider], typer.Option(
        "--provider", "-p", case_sensitive=False, help="Overwrites LLM_PROVIDER.",
    )] = None,
    model: Annotated[Optional[str], typer.Option(
        "--model", "-m", help="Overrides the provider's model.",
    )] = None,
    language: Annotated[Optional[str], typer.Option(
        "--language", "-l", help="Audio language (e.g., 'en'). Auto-detect if omitted.",
    )] = None,
    save_trascript: Annotated[bool, typer.Option(
        "--save-transcript", help="Also save the raw transcript.",
    )] = False,
) -> None:
    """It transcribes the input (if audio/video) and generates the content in the chosen format."""

    settings = get_settings()
    _setup_logging(settings.log_level)
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Testo sorgente
    if input_path.suffix.lower() in TEXT_EXTENSIONS:

        source_text = input_path.read_text(encoding="utf-8")

    else:

        source_text = _transcribe(Transcriber.from_settings(settings), input_path, language)

        if save_trascript:

            transcript_path = settings.output_dir / f"{input_path.stem}_transcript.txt"
            transcript_path.write_text(source_text, encoding="utf-8")
            console.print(f"[dim]Transcript saved in {transcript_path}[/dim]")

    # 2. Generazione
    try:

        generator = ContentGenerator.from_settings(settings, provider=provider, model=model)

        with console.status(f"[bold green]Content generation '{target}'..."):

            content = generator.generate(source_text, target)

    except ConfigurationError as exc:

        console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    # 3. Output
    out_path = output or settings.output_dir / f"{input_path.stem}_{target}.md"
    out_path.write_text(content, encoding="utf-8")
    console.rule(f"[bold]{TEMPLATES[target].label}")
    console.print(Markdown(content))
    console.print(f"[green]Saved in:[/green] {out_path}")


@app.command("list-targets")
def list_targets() -> None:
    """List the available output formats."""

    table = Table("Target", "Description")
    
    for key in available_targets():

        table.add_row(key, TEMPLATES[key].label)

    console.print(table)