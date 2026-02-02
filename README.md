# PlayLingo — Oyun için Çeviri Aracı
![.NET CI](https://github.com/dusunuryusuf5-byte/Projelerim/actions/workflows/dotnet.yml/badge.svg) ![Python CI](https://github.com/dusunuryusuf5-byte/Projelerim/actions/workflows/ci.yml/badge.svg)

Kısa ve çevrimdışı bir oyun çeviri aracı.

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

## Hata ayıklama 🔧
- VS Code'da `Python: Pytest` konfigürasyonunu kullanarak testleri hata ayıklayabilirsiniz.
- GitHub Actions: `.github/workflows/ci.yml` her `push` ve `pull_request` için testleri çalıştırır.

---
