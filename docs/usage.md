# Usage

## Python

Install dependencies and run tests:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Example:

```python
from playlingo import translate
from playlingo.subtitles import translate_subtitles

print(translate("hello", src="en", dest="tr"))
```

## .NET

Build and test:

```bash
# build
dotnet build src/PlayLingo

# test
dotnet test tests/PlayLingo.Tests
```

CLI example (translate SRT):

```bash
dotnet run --project src/PlayLingo -- translate-srt --input in.srt --output out.srt --src en --dest tr
```
