from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from anime_data import characters
from tourism_data import countries
from cars_data import cars
from ai_data import ais
from products_data import products
from stocks_data import stocks
from news_data import news_list, search_news
from japan_data import japan_info
from education_data import education
from api_helpers import get_stock_quote, get_news, get_anime_character, get_country, ask_ai
from translations import get_text

app = Flask(__name__)
app.secret_key = "narutofoxs_secret_key_2026"

def current_lang():
    return session.get("lang", "uz")

def t():
    return get_text(current_lang())

@app.route("/set_lang/<lang>")
def set_lang(lang):
    if lang in ("uz", "en", "ja"):
        session["lang"] = lang
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/")
def home():
    return render_template("index.html", t=t(), lang=current_lang())

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("dashboard"))
    return render_template("login.html", t=t(), lang=current_lang())

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return redirect(url_for("dashboard"))
    return render_template("register.html", t=t(), lang=current_lang())

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", t=t(), lang=current_lang())

@app.route("/anime", methods=["GET", "POST"])
def anime():
    result = None
    searched = False
    if request.method == "POST":
        searched = True
        name = request.form.get("character", "").strip().lower()
        if name in characters:
            result = characters[name]
        if not result:
            result = get_anime_character(name)
    return render_template("anime.html", result=result, searched=searched, t=t(), lang=current_lang())

@app.route("/tourism", methods=["GET", "POST"])
def tourism():
    result = None
    searched = False
    if request.method == "POST":
        searched = True
        name = request.form.get("country", "").strip().lower()
        result = get_country(name)
        local = countries.get(name)
        if not local and result:
            for k, v in countries.items():
                if result.get("name", "").lower() in (k, str(v.get("name", "")).lower()):
                    local = v
                    break
        if result and local:
            places = local.get("places") or local.get("info")
            if places:
                result["places"] = places
        if not result and name in countries:
            result = countries[name]
    return render_template("tourism.html", result=result, searched=searched, t=t(), lang=current_lang())

@app.route("/cars", methods=["GET", "POST"])
def cars_page():
    result = None
    searched = False
    if request.method == "POST":
        searched = True
        name = request.form.get("query", "").strip().lower()
        if name in cars:
            result = cars[name]
    return render_template("cars.html", result=result, searched=searched, t=t(), lang=current_lang())

@app.route("/ai", methods=["GET", "POST"])
def ai_page():
    result = None
    searched = False
    if request.method == "POST":
        searched = True
        name = request.form.get("ai_name", "").strip().lower()
        if name in ais:
            result = ais[name]
    return render_template("ai.html", result=result, searched=searched, t=t(), lang=current_lang())

@app.route("/chat", methods=["GET", "POST"])
def chat_page():
    answer = None
    question = ""
    if request.method == "POST":
        question = request.form.get("message", "").strip()
        if question:
            answer = ask_ai(question)
    return render_template("chat.html", answer=answer, question=question, t=t(), lang=current_lang())

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"ok": False, "answer": "Savol yozing."}), 400
    answer = ask_ai(message)
    return jsonify({"ok": True, "answer": answer})

@app.route("/products", methods=["GET", "POST"])
def products_page():
    result = None
    searched = False
    if request.method == "POST":
        searched = True
        name = request.form.get("product", "").strip().lower()
        if name in products:
            result = products[name]
    return render_template("products.html", result=result, searched=searched, t=t(), lang=current_lang())

@app.route("/stocks", methods=["GET", "POST"])
def stocks_page():
    result = None
    searched = False
    if request.method == "POST":
        searched = True
        name = request.form.get("stock", "").strip().lower()
        result = get_stock_quote(name)
        if not result and name in stocks:
            result = stocks[name]
    return render_template("stocks.html", result=result, searched=searched, t=t(), lang=current_lang())

@app.route("/news", methods=["GET", "POST"])
def news_page():
    results = None
    searched = False
    if request.method == "POST":
        searched = True
        topic = request.form.get("topic", "").strip() or "technology"
        results = get_news(topic)
        if not results:
            results = search_news(topic)
    return render_template(
        "news.html",
        results=results,
        searched=searched,
        default_news=news_list[:6],
        t=t(),
        lang=current_lang(),
    )

@app.route("/japan", methods=["GET", "POST"])
def japan_page():
    result = None
    searched = False
    if request.method == "POST":
        searched = True
        name = request.form.get("query", "").strip().lower()
        if name in japan_info:
            result = japan_info[name]
    return render_template("japan.html", result=result, searched=searched, t=t(), lang=current_lang())

@app.route("/education", methods=["GET", "POST"])
def education_page():
    result = None
    searched = False
    if request.method == "POST":
        searched = True
        name = request.form.get("topic", "").strip().lower()
        if name in education:
            result = education[name]
    return render_template("education.html", result=result, searched=searched, t=t(), lang=current_lang())

@app.route("/auth/google")
def auth_google():
    return redirect(url_for("dashboard"))

@app.route("/auth/apple")
def auth_apple():
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)