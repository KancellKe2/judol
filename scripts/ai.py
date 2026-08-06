import os
import json
import requests

# Konfigurasi OmniRoute
OMNI_API_KEY = os.environ.get("OMNI_API_KEY", "")
OMNI_BASE_URL = os.environ.get("OMNI_BASE_URL") or "https://ai.kancell.qzz.io/v1"
OMNI_MODEL = os.environ.get("OMNI_MODEL") or "omniroute"

def call_omniroute(prompt, system=None, max_tokens=512, temperature=0.2):
    """
    Kirim prompt ke OmniRoute API (OpenAI-compatible).
    """
    if not OMNI_API_KEY:
        print("[!] OMNI_API_KEY belum diset")
        return None

    url = f"{OMNI_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OMNI_API_KEY}",
        "Content-Type": "application/json",
    }

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": OMNI_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        if resp.status_code != 200:
            print(f"[!] OmniRoute API error {resp.status_code}: {resp.text[:300]}")
            return None
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[!] OmniRoute request gagal: {e}")
        return None

def generate_keywords():
    """
    Minta AI membuat daftar keyword pencarian situs judol.
    """
    prompt = """Buatkan 40 kata kunci pencarian dalam bahasa Indonesia untuk menemukan situs judi online (slot, casino, togel, poker, bola). Variasikan dengan kombinasi kata: situs, agen, daftar, login, judi, bandar, terpercaya, gacor. Keluarkan sebagai daftar, satu kata kunci per baris, tanpa nomor atau simbol."""

    system = "Anda adalah asisten yang andal dalam menghasilkan daftar kata kunci pencarian."

    text = call_omniroute(prompt, system=system, max_tokens=512, temperature=0.5)
    if not text:
        return None

    keywords = [line.strip() for line in text.splitlines() if line.strip()]
    return keywords

def classify_judol(text):
    """
    Minta AI menentukan apakah sebuah website adalah judol.
    Output: dict atau None
    """
    prompt = f"""Anda adalah sistem keamanan siber. Analisis konten website berikut dan tentukan apakah ini situs perjudian online (judi online, slot, casino, togel, poker, taruhan bola). Perhatikan istilah seperti deposit, withdraw, bonus, live casino, bandar, dll. Jawab dalam format JSON:
{{
  "is_judol": true/false,
  "confidence": 0.0-1.0,
  "reason": "alasan singkat"
}}

Konten website:
\"\"\"
{text[:3000]}
\"\"\"

Jawab JSON:"""

    system = "Anda adalah sistem keamanan siber yang menganalisis konten website."

    resp_text = call_omniroute(prompt, system=system, max_tokens=256, temperature=0.0)
    if not resp_text:
        return None

    # Bersihkan jika dibungkus ```json
    resp_text = resp_text.strip()
    if resp_text.startswith("```"):
        resp_text = resp_text.split("\n", 1)[1]
        resp_text = resp_text.rsplit("```", 1)[0]

    try:
        return json.loads(resp_text)
    except Exception:
        start = resp_text.find("{")
        end = resp_text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(resp_text[start:end])
            except Exception:
                return None
    return None
