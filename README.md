# PlayLingo — Oyun için Çeviri Aracı
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
Bu proje basit bir çeviri aracını içerir (`translator` paketi). Şu an için küçük, çevrimdışı bir sözlük kullanılıyor; örnek kullanım:

```python
from playlingo import translate

print(translate("hello", src="en", dest="tr"))  # -> "merhaba"
print(translate("merhaba", src="tr", dest="en"))  # -> "hello"
```

Desteklenen diller: `en`, `tr`.

---

## Hata ayıklama 🔧
- VS Code'da `Python: Pytest` konfigürasyonunu kullanarak testleri hata ayıklayabilirsiniz.
- GitHub Actions: `.github/workflows/ci.yml` her `push` ve `pull_request` için testleri çalıştırır.

---
