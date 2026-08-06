# Judol AdBlock List

Daftar blokir domain judi online (judol) untuk AdGuard Home.
Diperbarui otomatis setiap 6 jam menggunakan GitHub Actions dan AI OmniRoute.

## Cara Tambahkan ke AdGuard Home

1. Buka AdGuard Home Dashboard.
2. Pergi ke **Filter** → **DNS blocklists**.
3. Klik **Add blocklist** → **Add with URL**.
4. Masukkan URL:
https://kancellke2.github.io/judol/output/judol.txt
   atau jika pakai Cloudflare Pages:

https://judol-adblock.pages.dev/judol.txt

5. Simpan dan perbarui.

## Menjalankan Secara Manual

```bash
pip install -r scripts/requirements.txt
export OMNI_API_KEY="token-omniroute-kamu"
export OMNI_MODEL="nama-model"
python scripts/collect.py
python scripts/verify_ai.py
python scripts/generate_list.py

