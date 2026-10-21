import os
import requests

# Lokal config.py yoki Render Environment Variables
try:
    from config import FINNHUB_API_KEY, NEWS_API_KEY, OPENROUTER_API_KEY
except ImportError:
    FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")
    NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")


def get_stock_quote(symbol):
    """Finnhub orqali aksiya narxi"""
    symbol = (symbol or "").strip().upper()
    if not symbol:
        return None
    if not FINNHUB_API_KEY:
        return None
    try:
        url = "https://finnhub.io/api/v1/quote"
        r = requests.get(url, params={"symbol": symbol, "token": FINNHUB_API_KEY}, timeout=10)
        data = r.json()
        if r.status_code != 200 or data.get("c") is None:
            return None
        return {
            "symbol": symbol,
            "price": data.get("c"),
            "change": data.get("d"),
            "percent": data.get("dp"),
            "high": data.get("h"),
            "low": data.get("l"),
            "open": data.get("o"),
            "prev_close": data.get("pc"),
            "source": "Finnhub",
        }
    except Exception:
        return None


def get_news(topic="technology"):
    """NewsAPI orqali yangiliklar"""
    if not NEWS_API_KEY:
        return None
    try:
        url = "https://newsapi.org/v2/everything"
        r = requests.get(
            url,
            params={
                "q": topic,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 8,
                "apiKey": NEWS_API_KEY,
            },
            timeout=12,
        )
        data = r.json()
        if r.status_code != 200 or data.get("status") != "ok":
            return None
        results = []
        for a in data.get("articles", [])[:8]:
            results.append({
                "title": a.get("title") or "",
                "description": a.get("description") or "",
                "source": (a.get("source") or {}).get("name", ""),
                "url": a.get("url") or "",
                "date": (a.get("publishedAt") or "")[:10],
            })
        return results or None
    except Exception:
        return None


def get_anime_character(name):
    """Jikan API — personaj qidiruv"""
    name = (name or "").strip()
    if not name:
        return None
    try:
        url = "https://api.jikan.moe/v4/characters"
        r = requests.get(url, params={"q": name, "limit": 1}, timeout=12)
        data = r.json()
        items = data.get("data") or []
        if not items:
            return None
        c = items[0]
        img = ((c.get("images") or {}).get("jpg") or {}).get("image_url")
        return {
            "name": c.get("name") or name,
            "anime": "MyAnimeList / Jikan",
            "info": (c.get("about") or "")[:500] or "Ma'lumot topilmadi.",
            "image": img,
            "url": c.get("url"),
        }
    except Exception:
        return None


def get_country(name):
    """Davlat ma'lumoti (RestCountries / countries.dev)"""
    name = (name or "").strip()
    if not name:
        return None
    try:
        url = f"https://restcountries.com/v3.1/name/{name}"
        r = requests.get(url, params={"fullText": "false"}, timeout=12)
        if r.status_code != 200:
            return None
        data = r.json()
        if not data:
            return None
        c = data[0]
        capitals = c.get("capital") or []
        langs = c.get("languages") or {}
        return {
            "name": (c.get("name") or {}).get("common") or name,
            "capital": capitals[0] if capitals else "",
            "region": c.get("region") or "",
            "population": c.get("population"),
            "languages": ", ".join(langs.values()) if langs else "",
            "flag": (c.get("flags") or {}).get("png") or "",
            "info": f"Poytaxt: {capitals[0] if capitals else '—'}. Mintaqa: {c.get('region', '—')}.",
        }
    except Exception:
        return None


def ask_ai(user_message):
    """OpenRouter orqali AI javob"""
    key = (OPENROUTER_API_KEY or "").strip().strip('"').strip("'")
    if not key or len(key) < 20:
        return "OPENROUTER_API_KEY topilmadi. Render Environment Variables ni tekshiring."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://narutofoxs.onrender.com",
        "X-Title": "Narutofoxs",
    }
    system = (
        "Sen Narutofoxs sayti uchun yordamchi AI san. "
        "Faqat to'g'ri o'zbek tilida yoz. Imlo xatosiz, aniq va qisqa javob ber. "
        "So'zlarni buzma. Kod bo'lsa, toza Python/HTML/CSS misol ko'rsat. "
        "Bilmasang — 'aniq emas' de. Uydirma yozma."
    )
    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=45)
        data = r.json()
        if r.status_code != 200:
            err = data.get("error", {})
            msg = err.get("message") if isinstance(err, dict) else str(data)
            return f"Xato ({r.status_code}): {msg}"
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Ulanish xatosi: {e}"