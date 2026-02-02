# PlayLingo — Game-focused Translation Tool

A small offline translation toolkit for games. PlayLingo is available as both a Python package and a C#/.NET library.

## Quick start

### Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Example usage:

```python
from playlingo import translate
from playlingo.subtitles import translate_subtitles

print(translate("hello", src="en", dest="tr"))  # -> "merhaba"
```

### .NET (C#)

```bash
# build
dotnet build src/PlayLingo

# test
dotnet test tests/PlayLingo.Tests

# CLI (example)
dotnet run --project src/PlayLingo -- translate-srt --input in.srt --output out.srt --src en --dest tr
```

## What's included

- Python package `playlingo` with `translate(text, src, dest)` and `subtitles` helpers
- C# library `PlayLingo` with `Translator`, `Subtitles`, and CLI tools
- SRT parsing/serialization and field selection for subtitle translation
- Tests and CI workflows for both platforms

## License
MIT
