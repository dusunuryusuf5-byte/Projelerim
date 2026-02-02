# Projelerim
Çeviri yapma araci

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

## Hata ayıklama 🔧
- VS Code'da `Python: Pytest` konfigürasyonunu kullanarak testleri hata ayıklayabilirsiniz.
- GitHub Actions: `.github/workflows/ci.yml` her `push` ve `pull_request` için testleri çalıştırır.

---
