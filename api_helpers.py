import requests
from config import FINNHUB_API_KEY, NEWS_API_KEY

# Qidiruv so‘zini ticker ga aylantirish
SYMBOL_MAP = {
    "apple": "AAPL",
    "tesla": "TSLA",
    "nvidia": "NVDA",
    "microsoft": "MSFT",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "amazon": "AMZN",
    "meta": "META",
    "facebook": "META",
    "netflix": "NFLX",
    "amd": "AMD",
    "intel": "INTC",
    "toyota": "TM",
}

def get_stock_quote(query):
    """Finnhub dan aksiya narxini olish"""
    symbol = SYMBOL_MAP.get(query.lower().strip())
    if not symbol:
        # Agar xarita da bo‘lmasa, katta harf deb ticker deb sinab ko‘ramiz
        symbol = query.upper().strip()

    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    try:
        r = requests.get(url, timeout=8)
        data = r.json()
        # c = current price, d = change, dp = percent change
        if data.get("c") and data.get("c") > 0:
            change = data.get("d", 0)
            percent = data.get("dp", 0)
            direction = "up" if change >= 0 else "down"
            sign = "+" if change >= 0 else ""
            return {
                "name": symbol,
                "ticker": symbol,
                "price": f"${data['c']:.2f}",
                "change": f"{sign}{percent:.2f}%",
                "direction": direction,
                "sector": "Real-time (Finnhub)",
                "info": f"Joriy narx Finnhub API orqali olingan. Oldingi yopilish: ${data.get('pc', 0):.2f}"
            }
    except Exception:
        pass
    return None


def get_news(topic="technology"):
    """NewsAPI dan yangiliklar olish"""
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 8,
        "apiKey": NEWS_API_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data.get("status") == "ok" and data.get("articles"):
            results = []
            for a in data["articles"]:
                results.append({
                    "title": a.get("title") or "Sarlavha yo‘q",
                    "source": (a.get("source") or {}).get("name") or "Noma’lum",
                    "region": "API",
                    "date": (a.get("publishedAt") or "")[:10],
                    "summary": a.get("description") or a.get("content") or "Tavsif yo‘q",
                })
            return results
    except Exception:
        pass
    return None
def get_anime_character(query):
    """Jikan API (MyAnimeList) dan personaj qidirish"""
    url = "https://api.jikan.moe/v4/characters"
    params = {"q": query, "limit": 1}
    headers = {
        "User-Agent": "Narutofoxs/1.0"
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        data = r.json()
        if data.get("data") and len(data["data"]) > 0:
            c = data["data"][0]
            about = c.get("about") or "Ma’lumot topilmadi."
            if len(about) > 600:
                about = about[:600] + "..."
            image = None
            if c.get("images") and c["images"].get("jpg"):
                image = c["images"]["jpg"].get("image_url")
            return {
                "name": c.get("name") or query.title(),
                "anime": "MyAnimeList (Jikan API)",
                "info": about,
                "image": image,
                "url": c.get("url")
            }
    except Exception as e:
        print("Jikan xato:", e)
    return None
def get_country(query):
    """countries.dev API dan davlat ma'lumotini olish (bepul, kalit yo'q)"""
    name_map = {
        "turkiya": "turkey",
        "yaponiya": "japan",
        "fransiya": "france",
        "o'zbekiston": "uzbekistan",
        "ozbekiston": "uzbekistan",
        "uzbekistan": "uzbekistan",
        "italiya": "italy",
        "germaniya": "germany",
        "ispaniya": "spain",
        "angliya": "united kingdom",
        "britaniya": "united kingdom",
        "aqsh": "united states",
        "amerika": "united states",
        "koreya": "south korea",
        "janubiy koreya": "south korea",
        "xitoy": "china",
        "hindiston": "india",
        "rossiya": "russia",
        "misr": "egypt",
        "braziliya": "brazil",
        "kanada": "canada",
        "avstraliya": "australia",
    }
    q = query.lower().strip()
    search_name = name_map.get(q, q)

    url = f"https://countries.dev/name/{search_name}"
    headers = {"User-Agent": "Narutofoxs/1.0"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            c = data[0]
            name = c.get("name") or query.title()
            capital = c.get("capital") or "Noma'lum"
            if isinstance(capital, list):
                capital = ", ".join(capital)
            region = c.get("region") or "Noma'lum"
            population = c.get("population") or 0
            flag = None
            if c.get("flags"):
                flag = c["flags"].get("png") or c["flags"].get("svg")
            langs = c.get("languages") or []
            if isinstance(langs, list):
                languages = ", ".join(x.get("name", "") for x in langs if isinstance(x, dict)) or "Noma'lum"
            else:
                languages = str(langs)
            currs = c.get("currencies") or []
            if isinstance(currs, list):
                currency = ", ".join(
                    f"{x.get('name', '')} ({x.get('symbol', '')})" for x in currs if isinstance(x, dict)
                ) or "Noma'lum"
            else:
                currency = str(currs)
            return {
                "name": name,
                "places": f"Poytaxt: {capital}",
                "info": (
                    f"Mintaqa: {region}. Aholi: {population:,}. "
                    f"Tillar: {languages}. Valyuta: {currency}."
                ),
                "flag": flag,
                "capital": capital,
                "region": region,
                "population": f"{population:,}",
            }
    except Exception as e:
        print("countries.dev xato:", e)
    return None
def ask_ai(user_message):
    """OpenRouter orqali javob (bepul modellardan)"""
    try:
        from config import OPENROUTER_API_KEY
        key = (OPENROUTER_API_KEY or "").strip().strip('"').strip("'")
    except Exception as e:
        return f"config.py o‘qilmadi: {e}"

    if not key or len(key) < 20:
        return "OPENROUTER_API_KEY ni config.py ga to‘g‘ri qo‘ying."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://127.0.0.1:5000",
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