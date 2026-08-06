import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote, parse_qs
from pathlib import Path

from ai import generate_keywords
from keywords import SEARCH_KEYWORDS  # fallback

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DOMAINS_FILE = BASE_DIR / "raw_domains.txt"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def search_duckduckgo(keyword):
    """Cari domain dari DuckDuckGo HTML."""
    url = f"https://html.duckduckgo.com/html/?q={quote(keyword)}"
    domains = set()

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        for result in soup.select(".result__a"):
            href = result.get("href")
            if not href:
                continue

            # DuckDuckGo membungkus URL asli di parameter 'uddg='
            if "uddg=" in href:
                real_url = parse_qs(urlparse(href).query).get("uddg", [None])[0]
                if real_url:
                    domain = urlparse(real_url).netloc.lower()
                    if domain:
                        domains.add(domain)

    except Exception as e:
        print(f"[!] Error keyword '{keyword}': {e}")

    return domains

def main():
    # Ambil keyword dari AI, fallback ke manual
    keywords = generate_keywords()
    if not keywords:
        print("[!] Gagal dapat keyword dari AI, pakai manual.")
        keywords = SEARCH_KEYWORDS

    print(f"[*] Menggunakan {len(keywords)} keyword")

    all_domains = set()

    for kw in keywords:
        print(f"  → Mencari: {kw}")
        found = search_duckduckgo(kw)
        print(f"    Ditemukan: {len(found)} domain")
        all_domains.update(found)
        time.sleep(2)  # sopan ke server

    with open(RAW_DOMAINS_FILE, "w") as f:
        f.write("\n".join(sorted(all_domains)))

    print(f"\n[*] Total domain mentah: {len(all_domains)}")
    print(f"[*] Disimpan di {RAW_DOMAINS_FILE}")

if __name__ == "__main__":
    main()
