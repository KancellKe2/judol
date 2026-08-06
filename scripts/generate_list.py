from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
VERIFIED_DOMAINS_FILE = BASE_DIR / "verified_domains.txt"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_FILE = OUTPUT_DIR / "judol.txt"

def main():
    with open(VERIFIED_DOMAINS_FILE) as f:
        domains = [line.strip() for line in f if line.strip()]

    OUTPUT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    blocklist = [f"||{d}^" for d in sorted(set(domains))]

    with open(OUTPUT_FILE, "w") as f:
        f.write("# Judol AdBlock List\n")
        f.write(f"# Generated: {timestamp}\n")
        f.write(f"# Total: {len(blocklist)} domains\n")
        f.write("\n")
        f.write("\n".join(blocklist))

    print(f"[*] Berhasil generate {len(blocklist)} entri")
    print(f"[*] Disimpan di {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
