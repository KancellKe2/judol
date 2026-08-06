import os
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

from ai import classify_judol

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DOMAINS_FILE = BASE_DIR / "raw_domains.txt"
VERIFIED_DOMAINS_FILE = BASE_DIR / "verified_domains.txt"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def extract_text(html):
    """Ekstrak teks penting dari HTML."""
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string if soup.title else ""
    meta = ""
    desc = soup.find("meta", attrs={"name": "description"})
    if desc and desc.get("content"):
        meta = desc["content"]

    headings = []
    for h in soup.find_all(["h1", "h2", "h3"])[:5]:
        if h.get_text(strip=True):
            headings.append(h.get_text(strip=True))

    paras = []
    for p in soup.find_all("p")[:10]:
        if p.get_text(strip=True):
            paras.append(p.get_text(strip=True))

    return " | ".join([title, meta] + headings + paras)

def is_active(domain):
    """Cek apakah domain bisa diakses."""
    for scheme in ("https", "http"):
        try:
            resp = requests.get(
                f"{scheme}://{domain}",
                headers=HEADERS,
                timeout=10,
                allow_redirects=True,
            )
            if resp.status_code < 500 and resp.text:
                return True, resp.text
        except Exception:
            continue
    return False, ""

def main():
    with open(RAW_DOMAINS_FILE) as f:
        domains = [line.strip() for line in f if line.strip()]

    # Batasi verifikasi AI sesuai kuota
    max_verify = int(os.environ.get("MAX_VERIFY", "100"))
    print(f"[*] AI akan memverifikasi maksimal {max_verify} dari {len(domains)} domain mentah")

    verified = []
    count = 0

    for domain in domains:
        if count >= max_verify:
            print("[!] Batas verifikasi AI tercapai, berhenti.")
            break

        print(f"  → {domain}")

        active, html = is_active(domain)
        if not active:
            print("    ⛔ Tidak aktif, skip")
            continue

        text = extract_text(html)
        if not text:
            print("    ⛔ Tidak ada konten, skip")
            continue

        result = classify_judol(text)
        count += 1
        time.sleep(1.5)  # rate limit

        if result and result.get("is_judol"):
            conf = float(result.get("confidence", 0))
            if conf >= 0.7:
                print(f"    ✅ JUDOL (confidence: {conf})")
                verified.append(domain)
            else:
                print(f"    ? AI bilang judol tapi confidence rendah ({conf}), diabaikan")
        elif result:
            print(f"    ⛔ Bukan judol ({result.get('reason')})")
        else:
            print("    ⚠️ Gagal klasifikasi, dianggap non-judol")

    with open(VERIFIED_DOMAINS_FILE, "w") as f:
        f.write("\n".join(sorted(set(verified))))

    print(f"\n[*] Domain terverifikasi: {len(verified)}")
    print(f"[*] Disimpan di {VERIFIED_DOMAINS_FILE}")

if __name__ == "__main__":
    main()
