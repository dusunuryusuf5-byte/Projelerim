# PlayLingo — Oyun için Çeviri Aracı
![.NET CI](https://github.com/dusunuryusuf5-byte/Projelerim/actions/workflows/dotnet.yml/badge.svg) ![Python CI](https://github.com/dusunuryusuf5-byte/Projelerim/actions/workflows/ci.yml/badge.svg) ![Pages](https://github.com/dusunuryusuf5-byte/Projelerim/actions/workflows/pages.yml/badge.svg)

Kısa ve çevrimdışı bir oyun çeviri aracı. Site: https://dusunuryusuf5-byte.github.io/Projelerim/ (yayınlandıktan sonra geçerli olacaktır)

## Kurulum ve testler ✅
1. Sanal ortam oluşturun:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Bağımlılıkları yükleyin:

   ```bash
   pip install -r requirements.txt
   ```

3. Testleri çalıştırın:

   ```bash
   pytest
   ```

  ### Sistem geneli kurulum

  Linux/macOS (önerilen):

  ```bash
  ./setup.sh          # oluşturur ve bağımlılıkları yükler
  ./install.sh        # sistem launcherlari oluşturur (sudo gerekebilir)
  ```

  Windows:

  ```bat
  setup.bat
  install.bat         # proje kökünde run_playlingo.bat dosyalarını oluşturur
  ```

## Çeviri ✨
Bu proje basit bir çeviri aracını içerir. Hem **Python** (playlingo) hem de **C#/.NET** (PlayLingo) sürümleri bulunmaktadır.

### .NET (C#) kullanım örneği
Aşağıdaki örnek `PlayLingo` .NET kütüphanesini kullanır (CLI `translate-srt` komutu SRT dosyalarını çevirir):

```bash
# build
dotnet build src/PlayLingo

# test
dotnet test tests/PlayLingo.Tests

# CLI (örnek)
dotnet run --project src/PlayLingo -- translate-srt --input in.srt --output out.srt --src en --dest tr
```

Desteklenen diller: `en`, `tr`.

---

## Neler eklendi (kısa) ✅
Aşağıdaki özellikleri ekledim ve test ettim:

- **Python paket** `playlingo`:
  - `translate(text, src, dest)` fonksiyonu
  - `subtitles.translate_subtitles(...)` — altyazı koleksiyonlarını alan seçimi ile çevirme
  - `playlingo.cli` — SRT dosyalarını çeviren CLI (örnek: `python` ile çalıştırılabilir)
  - `tests/` içinde `pytest` tabanlı birim testleri ve `tests/conftest.py` ile `src/` import desteği
  - VS Code debug konfigürasyonu (`.vscode/launch.json`)

- **C#/.NET kütüphanesi** `PlayLingo`:
  - `Translator`, `Subtitles` sınıfları ve `Program` CLI
  - SRT okuma/yazma ve `TranslateSubtitles` (alan seçimi: `text` veya `caption`)
  - xUnit testleri (`tests/PlayLingo.Tests`) ve `.github/workflows/dotnet.yml` CI

- **Altyapı ve yardımcılar**:
  - `providers` arayüzü ve minimal `DeepLProvider` (örnek, API anahtarı ile kullanılır)
  - `start.bat` — Windows için CLI kolay başlatma (dotnet run wrapper)
  - CI: Python ve .NET için GitHub Actions workflow'ları (badge'ler README'e eklendi)

## Hızlı kullanım örnekleri 🧪
- Python (örnek):

```python
from playlingo import translate
from playlingo.subtitles import translate_subtitles

print(translate("hello", src="en", dest="tr"))
# SRT çevirisi:
# subs = srt_to_subs(open("in.srt").read())
# out = translate_subtitles(subs, src="en", dest="tr")
```

- .NET CLI (örnek):

```bash
dotnet run --project src/PlayLingo -- translate-srt --input in.srt --output out.srt --src en --dest tr
```

---

## GUI: Hızlı Çeviri Aracı 🖥️
- Basit bir GUI uygulaması eklendi (`playlingo.gui`) — kopyaladığınız metni hızlıca çevirir ve SRT dosyanızı "monitor" modunda gerçek zamanlı olarak izleyip altyazı göründüğünde çevirisini overlay pencerede gösterir.
- Overlay görünümü özelleştirilebilir: arka plan rengi, metin rengi, font aile/size ve transparanlık ayarlanabilir. Ayarlar penceresini `Settings` butonundan açabilirsiniz; ayarlar `~/.playlingo_overlay.json` içinde saklanır.
- Çalıştırma (Windows): `start_gui.bat` — veya `python -m playlingo.gui` (her platformda çalışır).

## Kurulum (setup) ⚙️
- Linux / macOS
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
- Windows
  ```bat
  setup.bat
  ```

## Başlatma
- GUI: `python -m playlingo.gui` veya Windows'ta `start.bat gui` veya `start_gui.bat`
- GUI (debug): `start_debug.sh` (Linux/macOS), `start_debug.bat` (Windows), veya VS Code'da `Python: Run PlayLingo GUI (Debug)` konfigürasyonu
- Run tests (debug): `run_tests_debug.sh` / `run_tests_debug.bat` — `PLAYLINGO_DEBUG=1` altında testleri çalıştırır ve in-memory logs toplayacaktır.
- CLI (.NET): `start.bat translate-srt --input in.srt --output out.srt --src en --dest tr`

## Hata ayıklama 🔧
- VS Code: `Python: Pytest`, `Python: Run PlayLingo GUI` ve `C# .NET: Launch PlayLingo` konfigürasyonları eklendi; GUI ve .NET uygulamaları debug modda çalıştırılabilir.
- GitHub Actions: `.github/workflows/ci.yml` ve `.github/workflows/dotnet.yml` her `push` ve `pull_request` için testleri çalıştırır.

- Lokal debug (GUI): `PLAYLINGO_DEBUG=1 python -m playlingo.gui` veya `./start_debug.sh` ile debug seviyesinde log alabilirsiniz.

---
