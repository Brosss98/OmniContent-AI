# OmniContent AI

**Turn audio, video and text into ready-to-publish posts, threads and newsletters — 100% locally, or with your own API keys.**

OmniContent AI is an open-source Python tool that transcribes media files with [faster-whisper](https://github.com/SYSTRAN/faster-whisper) and rewrites the result into structured content for social media, blogs and newsletters using an LLM of your choice.

- 🔒 **Privacy-first** — run everything offline with [Ollama](https://ollama.com). No account, no SaaS, no data leaving your machine.
- 🔑 **Bring your own key** — optionally switch to OpenAI or Anthropic with a single setting.
- 🧩 **Modular** — output formats are plain, validated templates: adding a new one takes a few lines.
- 💻 **Simple** — one CLI command today, a minimal Streamlit UI on the roadmap.

> **Status:** early development (v0.1). See the [Roadmap](#roadmap) for what is and isn't implemented yet.

---

## Table of contents

- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Setting up the LLM (Ollama or API keys)](#setting-up-the-llm)
- [Usage](#usage)
- [Configuration reference](#configuration-reference)
- [Output formats](#output-formats)
- [GPU acceleration (optional)](#gpu-acceleration-optional)
- [Project structure](#project-structure)
- [FAQ & troubleshooting](#faq--troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## How it works

```
 audio / video ──► faster-whisper ──► transcript ─┐
                                                  ├──► LLM (Ollama | OpenAI | Anthropic) + template ──► Markdown output
 .txt / .md ──────────────────────────────────────┘
```

1. **Input** — an audio/video file (`.mp3`, `.wav`, `.m4a`, `.mp4`, `.mkv`, …) or a text file (`.txt`, `.md`).
2. **Transcription** — media files are transcribed locally by faster-whisper (language auto-detected). Text files skip this step.
3. **Generation** — the text is sent to the configured LLM together with the template of the chosen target (e.g. `linkedin`).
4. **Output** — the result is printed in the terminal and saved as Markdown in `output/`.

---

## Requirements

| Requirement | Notes |
|---|---|
| **Python 3.10 – 3.13** | Python 3.14 is not supported yet (see [FAQ](#python-314-pip-asks-for-microsoft-c-build-tools)). |
| **Git** | To clone the repository. |
| **Ollama** | Only for local/offline LLMs. Not needed if you use OpenAI or Anthropic. |
| **Disk space** | Whisper models: ~75 MB (`tiny`) to ~3 GB (`large-v3`). Ollama models: typically 2–8 GB. |
| **NVIDIA GPU** | Optional. Everything runs on CPU. |

**FFmpeg is not required** for transcribing local files: faster-whisper decodes audio through PyAV, which ships its own FFmpeg libraries.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Brosss98/omnicontent-ai.git
cd omnicontent-ai
```

### 2. Create and activate a virtual environment

**Windows (PowerShell)**
```powershell
py -3.13 -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

> On Windows, if activation is blocked by the execution policy, run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 3. Install the dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create your configuration file

```bash
# Windows
copy .env.example .env
# Linux / macOS
cp .env.example .env
```

Then open `.env` and adjust it (see [Configuration reference](#configuration-reference)). The defaults work out of the box with Ollama and `llama3.1:8b`.

---

## Setting up the LLM

### Option A — Local and offline with Ollama (default)

1. **Install Ollama** from [ollama.com/download](https://ollama.com/download) (Windows, macOS, Linux).
2. **Make sure the Ollama server is running.** The desktop app starts it automatically; otherwise run:
   ```bash
   ollama serve
   ```
3. **Pull the model *before* running OmniContent AI.** The model name must match `OLLAMA_MODEL` in your `.env`:
   ```bash
   ollama pull llama3.1:8b
   ```
4. **Verify** the model is available:
   ```bash
   ollama list
   ```

> ⚠️ OmniContent AI does **not** download Ollama models for you. If the model has not been pulled, generation fails with a "model not found" error.

Any chat model available in Ollama works. Pick one according to your hardware — smaller models (3–8B parameters) run fine on a laptop, larger ones give better writing quality but need more RAM/VRAM. To use a different model, pull it and update `OLLAMA_MODEL`, or pass it on the fly with `--model`.

### Option B — OpenAI

```ini
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### Option C — Anthropic

```ini
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-haiku-latest
```

> With API providers, the transcription still happens locally: only the **transcribed text** is sent to the provider. API usage is billed to your account.

---

## Usage

All commands are run from the repository root, with the virtual environment active.

### List available output formats

```bash
python main.py list-targets
```

### Transcribe and generate

```bash
python main.py transcribe-and-generate --input file.mp3 --target linkedin
```

### Command-line options

```bash
python main.py transcribe-and-generate --help
```

| Option | Short | Default | Description |
|---|---|---|---|
| `--input` | `-i` | *(required)* | Audio/video file, or a `.txt` / `.md` text file. |
| `--target` | `-t` | `linkedin` | Output format: `linkedin`, `twitter`, `newsletter`. |
| `--output` | `-o` | `OUTPUT_DIR/<input-name>_<target>.md` | Custom output file path. |
| `--provider` | `-p` | `LLM_PROVIDER` | Override the provider: `ollama`, `openai`, `anthropic`. |
| `--model` | `-m` | model set for the provider in `.env` | Override the LLM model name. |
| `--language` | `-l` | auto-detect | Spoken language of the audio (ISO code, e.g. `it`, `en`). Speeds up transcription and avoids wrong detection. |
| `--save-transcript` | | off | Also save the raw transcript to `OUTPUT_DIR/<input-name>_transcript.txt`. |

### Examples

```bash
# Local LinkedIn post from an Italian podcast, keeping the transcript
python main.py transcribe-and-generate -i podcast.mp3 -t linkedin -l it --save-transcript

# Twitter/X thread from a video, using OpenAI just for this run
python main.py transcribe-and-generate -i talk.mp4 -t twitter -p openai

# Newsletter from an existing transcript, with a different Ollama model
python main.py transcribe-and-generate -i notes.md -t newsletter -m qwen2.5:7b

# Custom output path
python main.py transcribe-and-generate -i webinar.wav -t newsletter -o drafts/issue-12.md
```

> 💡 **Tip:** transcription is the slow part. Use `--save-transcript` once, then feed the `.txt` back with `-i` to try different targets or models without transcribing again.

### Settings priority

**Command-line options** > **environment variables** > **`.env` file** > **built-in defaults**.

Only some settings have a CLI flag (provider, model, language). Everything else is configured through `.env` or environment variables — for example, for a single run:

```powershell
# Windows PowerShell
$env:WHISPER_MODEL="medium"; python main.py transcribe-and-generate -i file.mp3 -t linkedin
```
```bash
# Linux / macOS
WHISPER_MODEL=medium python main.py transcribe-and-generate -i file.mp3 -t linkedin
```

---

## Configuration reference

All settings live in `.env` (copied from `.env.example`). Names are case-insensitive. Empty values are ignored and fall back to the default.

### LLM

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | `ollama`, `openai` or `anthropic`. |
| `LLM_TEMPERATURE` | `0.7` | Creativity, from `0.0` (deterministic) to `2.0`. |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address. Change it to use Ollama on another machine. |
| `OLLAMA_MODEL` | `llama3.1:8b` | Must be pulled first with `ollama pull`. |
| `OPENAI_API_KEY` | — | Required only when the provider is `openai`. |
| `OPENAI_MODEL` | `gpt-4o-mini` | Any OpenAI chat model your key can access. |
| `ANTHROPIC_API_KEY` | — | Required only when the provider is `anthropic`. |
| `ANTHROPIC_MODEL` | `claude-3-5-haiku-latest` | Any Anthropic model your key can access. |

### Transcription (Whisper)

| Variable | Default | Description |
|---|---|---|
| `WHISPER_MODEL` | `small` | `tiny`, `base`, `small`, `medium`, `large-v3`, `distil-large-v3`. Bigger = more accurate but slower. |
| `WHISPER_DEVICE` | `auto` | `auto`, `cpu` or `cuda`. With `auto`, if CUDA libraries are missing the tool falls back to CPU. |
| `WHISPER_COMPUTE_TYPE` | `int8` | `int8` (fast, low memory, CPU or GPU), `float16` (GPU), `float32`. |

### Output

| Variable | Default | Description |
|---|---|---|
| `OUTPUT_DIR` | `output` | Folder for generated files (created automatically). |
| `OUTPUT_LANGUAGE` | `english` | Language of the generated content, as free text (`english`, `italiano`, `español`, …). It can differ from the audio language. |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`. |

---

## Output formats

| Target | Format | Main rules |
|---|---|---|
| `linkedin` | LinkedIn post | Short hook, 3–5 key insights, closing question/CTA, max 3 hashtags, ≤ 1300 characters. |
| `twitter` | Twitter/X thread | 4–8 numbered tweets, each under 280 characters, hook first and CTA last. |
| `newsletter` | Newsletter issue (Markdown) | Subject line, intro, H2 sections, "Key takeaways" box, closing. |

Want another format (blog post, YouTube description, Instagram caption…)? Templates are small Pydantic objects in `app/templates/` — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## GPU acceleration (optional)

Transcription works well on CPU. With an NVIDIA GPU it can be several times faster.

1. Install a recent NVIDIA driver.
2. Install the CUDA 12 / cuDNN 9 libraries via pip (no full CUDA Toolkit needed):
   ```bash
   pip install -r requirements-gpu.txt
   ```
3. Set in `.env`:
   ```ini
   WHISPER_DEVICE=cuda
   WHISPER_COMPUTE_TYPE=float16
   ```

On Windows, OmniContent AI automatically registers the DLL folders installed by the `nvidia-*` pip packages, so no manual `PATH` changes are required.

---

## Project structure

```
.
├── app/
│   ├── config.py             # Settings (pydantic-settings, reads .env)
│   ├── cli.py                # Typer CLI
│   ├── core/
│   │   ├── cuda_paths.py     # Windows: exposes pip-installed CUDA DLLs
│   │   ├── transcriber.py    # faster-whisper wrapper (lazy loading, CPU fallback)
│   │   └── generator.py      # LLM factory + prompt chain (LangChain)
│   ├── templates/            # Output formats (one file per target + registry)
│   └── ui/                   # Streamlit app (roadmap)
├── tests/
├── .env.example
├── requirements.txt
├── requirements-gpu.txt
├── pyproject.toml            # Project metadata, Pyright and pytest config
└── main.py                   # Entrypoint
```

---

## FAQ & troubleshooting

### Is it really 100% offline?
Yes, with `LLM_PROVIDER=ollama`. The only network access is the **first-time download** of the Whisper model from Hugging Face and of the Ollama model via `ollama pull`. After that, both are cached locally and no data leaves your machine.

### Where are the Whisper models stored? Can I delete them?
In the Hugging Face cache (`~/.cache/huggingface/hub`, on Windows `C:\Users\<you>\.cache\huggingface\hub`). You can delete them safely; they are downloaded again on next use.

### The first run is very slow / seems stuck.
It is downloading the Whisper model. Later runs start immediately. Ollama also needs a few seconds to load the model into memory on the first request.

### Which Whisper model should I use?
`small` is a good balance on CPU. Use `base`/`tiny` for speed on weak machines, `medium` or `large-v3` (ideally on GPU) for the best accuracy, especially with accents or technical vocabulary.

### `Connection refused` / cannot connect to `localhost:11434`
The Ollama server is not running. Start the Ollama app or run `ollama serve`, then check `OLLAMA_BASE_URL`.

### `model "xxx" not found` with Ollama
You have not pulled the model, or the name in `OLLAMA_MODEL` is different from the one in `ollama list`. Run `ollama pull <model>`.

### `OPENAI_API_KEY mancante` / `ANTHROPIC_API_KEY mancante`
You selected an API provider (in `.env` or with `--provider`) but the matching key is empty in `.env`.

### `TypeError: open() got an unexpected keyword argument 'metadata_errors'`
PyAV 19 removed a parameter still used by faster-whisper 1.2.x. `requirements.txt` already pins `av<19`; if you installed packages manually, run:
```bash
pip install "av<19" --force-reinstall
```

### Python 3.14: pip asks for Microsoft C++ Build Tools
PyAV versions below 19 have no prebuilt wheels for Python 3.14, so pip tries to compile them. Recreate the virtual environment with Python 3.13 (`py -3.13 -m venv .venv`).

### `RuntimeError: Library cublas64_12.dll is not found`
A GPU was detected but the CUDA 12 libraries are missing. Either set `WHISPER_DEVICE=cpu`, or follow [GPU acceleration](#gpu-acceleration-optional). With `WHISPER_DEVICE=auto` the tool falls back to CPU automatically.

### Errors mentioning `cudnn_ops64_9.dll` or other cuDNN files
The installed cuDNN version does not match the one expected by your `ctranslate2` version. Check `pip show ctranslate2` and install the matching `nvidia-cudnn-cu12` version, or use the CPU.

### Long recordings: the output ignores the end of the audio
In v0.1 the whole transcript is sent in a single prompt. Local models with a small context window may truncate very long transcripts (roughly over one hour of speech). Chunked map-reduce summarisation is on the roadmap. Meanwhile, use a model with a larger context or split the audio.

### Can the audio be in one language and the output in another?
Yes. The audio language is auto-detected (or set with `--language`), while the output language is set by `OUTPUT_LANGUAGE`.

### Can I use Ollama running on another computer or server?
Yes: set `OLLAMA_BASE_URL=http://<host>:11434` and make sure that Ollama accepts remote connections on that host.

### Are my API keys safe?
Keys are only read from your local `.env` / environment variables and handled as secret values (never printed in logs). `.env` is listed in `.gitignore`: **never commit it**.

---

## Roadmap

- [x] Local transcription with faster-whisper (CPU/GPU, automatic CPU fallback)
- [x] Ollama, OpenAI and Anthropic providers
- [x] LinkedIn, Twitter/X and newsletter templates
- [x] Typer CLI
- [ ] YouTube / URL input via `yt-dlp` (`app/core/downloader.py`)
- [ ] Chunking + map-reduce for long transcripts
- [ ] Streamlit web UI
- [ ] More templates (blog post, YouTube description, Instagram caption)
- [ ] Custom user templates loaded from YAML files
- [ ] Docker image

---

## Contributing

Contributions are welcome! Read [CONTRIBUTING.md](CONTRIBUTING.md) to get started — adding a new output template is the easiest first contribution.

## License

Licensed under the [Apache License 2.0](LICENSE). You are free to use, modify and redistribute this software, including commercially, provided that you keep the copyright and [NOTICE](NOTICE) file and state your changes.

The name **"OmniContent AI"** is not covered by the license: forks and derivative works must use a different name.

## Acknowledgements

[faster-whisper](https://github.com/SYSTRAN/faster-whisper) · [Ollama](https://ollama.com) · [LangChain](https://github.com/langchain-ai/langchain) · [Typer](https://github.com/fastapi/typer) · [yt-dlp](https://github.com/yt-dlp/yt-dlp) · [Streamlit](https://streamlit.io)
