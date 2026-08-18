QA_MODEL = "gpt-5.4"

WEB_SEARCH_MODEL = "gpt-5.4"

WEB_MAX_TOKENS = 500

GPT_RETRY_COUNT = 1

GPT_RETRY_DELAY_MS = 900

SYSTEM_PROMPT = ("Turkce yanit ver. Cevabini OZET halinde ver: ana noktalari "
                 "kisaca topla. SADECE duz metin: madde isareti, yildiz (*), "
                 "baslik (#) veya tablo KULLANMA. "
                 "Kullaniciya kesinlikle soru sorma veya secenek sunma. "
                 "Soru belirsizse en makul varsayimi yapip dogrudan cevapla. "
                 "Guncel veriye erisemesen bile erisemiyorum deme; en son "
                 "bildigin bilgiyi tarihini acikca belirterek cevapla. "
                 "COK ONEMLI KURAL: Cevabinda kesinlikle URL, site adi veya "
                 "kaynak belirtme. 'Kaynaklara gore', 'haberlere gore', "
                 "'verilere gore', 'X sitesine gore', 'arastirmalara gore' "
                 "gibi ifadeleri KULLANMA. Bilgiyi kaynak belirtmeden, sanki "
                 "kendin biliyormus gibi dogrudan soyle. Bilginin nereden "
                 "alindigini hicbir sekilde aciklama; kurum, haber kurumu, "
                 "web sitesi, platform, kaynak, alinti veya arama sonucu "
                 "adi verme. "
                 "Cevabinin en sonunda, sadece verdigin bilginin hangi yila "
                 "ait oldugunu kisa bir cumleyle belirt (kaynak degil, sadece yil).")

WEB_SYSTEM_PROMPT = (
    "Turkce ve yalnizca duz metin cevap ver. En fazla 1-3 kisa cumle kullan. "
    "Web arama aracini mutlaka kullan; guncel sorularda model bellegine "
    "dayanma. Yayin veya guncellenme tarihi en yeni olan sonucu sec. "
    "Kullaniciya kesinlikle soru sorma veya secenek sunma. Belirsiz bir haber "
    "sorusunda Turkiye ile ilgili en onemli guncel haberi secip cevapla. "
    "Guncel veriyi bulamazsan erisemiyorum veya dogrulayamiyorum deme; web "
    "aramasinda buldugun en yeni sonucu tarihini belirterek dogrudan ver. "
    "Mac ve fikstur sorularini sadece Super Lig ile sinirlama; UEFA, Avrupa "
    "ligleri, milli maclar ve Turkiye liglerinden en onemli maclari birlikte ver. "
    "URL, site veya kaynak adi yazma. Bilgiyi nereden aldigini soyleme; "
    "kurum, haber kurumu, platform, kaynak veya arama sonucu adi verme. "
    "Bugunun tarihi %s. En yeni tarihli "
    "guvenilir veriyi kullan; farkli tarihler varsa en guncelini sec. "
    "Son cumlede verinin tam tarihini belirt.")

MAX_TOKENS = 450

WEB_QUERY_HINTS = (
    "bugun", "bugunku", "yarin", "yarinki", "dun", "dunku", "guncel",
    "canli", "son durum", "son dakika", "su an", "simdi",
    "bu hafta", "bu ay", "bu yil", "en son", "hava", "yagmur",
    "sicaklik", "sogukluk", "nem", "ruzgar", "basinc", "uv", "gorus",
    "dolar", "euro", "avro", "altin", "gumus", "kur", "borsa",
    "hisse", "bitcoin", "btc", "ethereum", "eth", "kripto", "fiyat", "kac tl", "ne kadar",
    "haber", "haberler", "mac", "maclar", "skor", "skorlar",
    "puan durumu", "lig", "ligler", "fikstur", "fiksturler",
    "deprem", "depremler",
    "trafik", "kim kazandi", "secim", "sonuc", "sonuclar", "piyasa",
    "doviz", "enflasyon", "faiz", "zam", "resmi gazete",
    "cumhurbaskani", "baskani", "bakani", "ceo",
    "internetten", "webden", "ara", "kontrol et",
)

SPORTS_QUERY_HINTS = (
    "mac", "maclar", "skor", "skorlar", "puan durumu",
    "lig", "ligler", "fikstur", "fiksturler",
)

PRESET_Q = [
    ("BUGUN HAVA NASIL",
     lambda: USER_CITY + " icin bugunku hava durumunu TUM detaylariyla ver: "
             "su anki sicaklik, hissedilen sicaklik, gunun en yuksek ve en "
             "dusuk sicakligi, ruzgar hizini km/h olarak, ani ruzgar (gust) "
             "hizini km/h olarak ve yagis/yagmur ihtimalini soyle."),
    ("DOLAR VE EURO NE KADAR",
     "Dolar ve Euro'nun bugunku guncel alis ve satis kurlari ne kadar?"),
    ("GRAM ALTIN NE KADAR",
     "Gram altinin bugunku guncel fiyati ne kadar?"),
    ("SON DAKIKA HABERLER",
     "Turkiye'de bugunku onemli son dakika haberleri nelerdir?"),
    ("BUGUN NELER OLDU",
     "Bugun Turkiye'de ve dunyada onemli olarak neler oldu?"),
    ("BU HAFTA MACLAR",
     "Onumuzdeki bir hafta icinde oynanacak onemli futbol maclarini "
     "(ozellikle Turkiye Super Lig ve varsa milli mac / Avrupa kupalari) "
     "gun, tarih ve TSI baslama saatiyle birlikte liste halinde ver."),
]

# Bu modul clock_app'in isim alanindan calisir. Bagimliliklar acik yazilir ki
# eksik bir isim calisma aninda NameError yerine hemen ve anlasilir sekilde
# ortaya ciksin.
_REQUIRED = (
    "lcd", "touch", "time", "os", "gc", "json", "socket", "ssl",
    "OPENAI_API_KEY", "tls_connect", "log_error", "to_screen_text",
    "show_answer", "wrap_full", "_watchdog_touch", "_mini_saat",
    "WIDTH", "HEIGHT",
    "BG", "FG", "GRAY", "WHITE", "BLACK", "RED", "GREEN", "TITLE_COL",
)


def start(app):
    global _app
    _app = app
    here = globals()
    for name, value in app.__dict__.items():
        if name not in here:
            here[name] = value
    missing = [n for n in _REQUIRED if n not in here]
    if missing:
        raise RuntimeError("sor_feature eksik bagimlilik: " + ", ".join(missing))
    return _open_sor_impl()


def openai_chat(messages, model, web_search, timeout, max_tok=None,
                reasoning=None, search_context="low", on_delta=None):
    if socket is None or ssl is None:
        return None, "AG MODULU YOK"
    api_key = OPENAI_API_KEY.strip()
    if not api_key or api_key.startswith("sk-BURAYA"):
        return None, "API ANAHTARI GIRILMEMIS"
    mt = max_tok if max_tok is not None else MAX_TOKENS
    instructions = []
    request_input = []
    for message in messages:
        if message.get("role") == "system":
            instructions.append(message.get("content", ""))
        else:
            request_input.append(message)
    body = {
        "model": WEB_SEARCH_MODEL if web_search else model,
        "input": request_input,
        "max_output_tokens": min(mt, WEB_MAX_TOKENS) if web_search else mt,
    }
    if instructions:
        body["instructions"] = "\n".join(instructions)
    if reasoning:
        body["reasoning"] = {"effort": reasoning}
    if web_search:
        body["text"] = {"verbosity": "low"}
        body["tool_choice"] = "required"
        body["max_tool_calls"] = 1
        body["tools"] = [{
            "type": "web_search",
            "search_context_size": search_context,
            "user_location": {
                "type": "approximate",
                "country": USER_COUNTRY,
                "city": USER_CITY,
                "region": USER_REGION,
            },
        }]
    body["stream"] = True
    payload = json.dumps(body)
    body = None
    messages = None
    request_input = None
    instructions = None
    gc.collect()
    transient_status = (0, 408, 429, 500, 502, 503, 504)
    last_error = "BAGLANTI HATASI"
    attempt_count = 1 if web_search else GPT_RETRY_COUNT + 1
    try:
        import gpt_stream
    except Exception as exc:
        return None, "GPT MODULU: " + str(exc)
    try:
        for attempt in range(attempt_count):
            gc.collect()
            status = 0
            answer = None
            stream_error = None
            try:
                status, answer, stream_error = gpt_stream.post(
                    "api.openai.com", "/v1/responses", api_key, payload,
                    timeout, on_delta, _gpt_wait_step,
                    tls_connect=tls_connect)
            except Exception as exc:
                stream_error = "BAGLANTI HATASI: " + str(exc)
            gc.collect()
            if answer:
                return answer, None
            if stream_error:
                last_error = stream_error
            elif status in transient_status:
                last_error = "API GECICI HATA " + str(status)
            else:
                last_error = "API HATASI KOD " + str(status)
            if status not in transient_status and status != 200:
                return None, last_error
            if attempt + 1 < attempt_count:
                time.sleep_ms(GPT_RETRY_DELAY_MS)
        return None, last_error
    finally:
        gpt_stream = None
        try:
            import sys
            del sys.modules["gpt_stream"]
        except Exception:
            pass
        gc.collect()

def _normalize_question(q):
    text = str(q).lower()
    for src, dst in (
            ("ı", "i"), ("ş", "s"), ("ğ", "g"),
            ("ü", "u"), ("ö", "o"), ("ç", "c")):
        text = text.replace(src, dst)
    for separator in ".,?!:;()[]{}-/\\'\"":
        text = text.replace(separator, " ")
    return " " + " ".join(text.split()) + " "

def strip_source_disclosures(text):
    kept = []
    source_starts = (
        " kaynak ", " kaynaklar ", " bilgi kaynagi ",
        " veri kaynagi ", " web aramasi ", " alinti ",
    )
    for line in str(text).split("\n"):
        normalized = _normalize_question(line)
        if any(normalized.startswith(marker) for marker in source_starts):
            continue
        kept.append(line)
    return "\n".join(kept).strip()

def question_needs_web(q):
    text = _normalize_question(q)
    for hint in WEB_QUERY_HINTS:
        if " " + hint + " " in text:
            return True
    return False

def _question_is_sports(q):
    text = _normalize_question(q)
    for hint in SPORTS_QUERY_HINTS:
        if " " + hint + " " in text:
            return True
    return False

def _live_cache_path(q):
    text = _normalize_question(q)
    value = 2166136261
    for ch in text:
        value ^= ord(ch) & 0xFF
        value = (value * 16777619) & 0xFFFFFFFF
    return LIVE_CACHE_PREFIX + ("%08x" % value) + ".txt", text

def _live_cache_get(q):
    path, normalized = _live_cache_path(q)
    f = None
    try:
        now = int(time.time())
        if now < 100000:
            return None
        f = open(path, "r")
        saved = int(f.readline().strip())
        stored_q = f.readline().rstrip("\r\n")
        if stored_q != normalized or now < saved or now - saved > LIVE_CACHE_SECONDS:
            f.close()
            f = None
            try:
                os.remove(path)
            except Exception:
                pass
            return None
        answer = f.read(4096)
        f.close()
        return answer if answer else None
    except Exception:
        if f is not None:
            try:
                f.close()
            except Exception:
                pass
        return None

def _live_cache_trim():
    try:
        entries = []
        for name in os.listdir():
            if not name.startswith(LIVE_CACHE_PREFIX) or not name.endswith(".txt"):
                continue
            stamp = 0
            f = None
            try:
                f = open(name, "r")
                stamp = int(f.readline().strip())
                f.close()
                f = None
            except Exception:
                if f is not None:
                    try:
                        f.close()
                    except Exception:
                        pass
            entries.append((stamp, name))
        entries.sort()
        while len(entries) > LIVE_CACHE_LIMIT:
            _stamp, name = entries.pop(0)
            try:
                os.remove(name)
            except Exception:
                pass
    except Exception:
        pass

def _live_cache_put(q, answer):
    try:
        now = int(time.time())
        if now < 100000 or not answer:
            return
        path, normalized = _live_cache_path(q)
        safe_write_text(path, "%d\n%s\n%s" % (
            now, normalized, str(answer)[:4096]))
        _live_cache_trim()
    except Exception:
        pass

def _answer_refuses_current(answer):
    text = _normalize_question(answer)
    markers = (
        " dogrulayamiyorum ", " guncel veri alamiyorum ",
        " guncel veriye erisemiyorum ", " canli veriye erisimim yok ",
        " gercek zamanli veriye erisemiyorum ", " web erisimim yok ",
        " internete erisemiyorum ", " hangi kanal ", " hangi lig ",
    )
    for marker in markers:
        if marker in text:
            return True
    return False

def _today_text():
    try:
        lt = time.localtime()
        if 2024 <= lt[0] <= 2100:
            return "%04d-%02d-%02d" % (lt[0], lt[1], lt[2])
    except Exception:
        pass
    return "bilinmiyor"

def _display_date(value):
    try:
        parts = str(value)[:10].split("-")
        return "%s/%s/%s" % (parts[2], parts[1], parts[0])
    except Exception:
        return str(value)

def _weather_condition(code):
    try:
        code = int(code)
    except Exception:
        return ""
    if code == 0:
        return "acik"
    if code <= 2:
        return "parcali bulutlu"
    if code == 3:
        return "kapali"
    if code in (45, 48):
        return "sisli"
    if 51 <= code <= 57:
        return "ciseleyen"
    if 61 <= code <= 67:
        return "yagmurlu"
    if 71 <= code <= 77:
        return "karli"
    if 80 <= code <= 82:
        return "saganak yagisli"
    if code in (85, 86):
        return "kar saganakli"
    if 95 <= code <= 99:
        return "gok gurultulu"
    return ""

def _event_local_date_time(stamp):
    try:
        year = int(stamp[0:4])
        month = int(stamp[5:7])
        day = int(stamp[8:10])
        hour = int(stamp[11:13]) + 3
        minute = int(stamp[14:16])
        if hour >= 24:
            hour -= 24
            day += 1
            month_days = (31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30,
                          31, 31, 30, 31, 30, 31)
            if day > month_days[month - 1]:
                day = 1
                month += 1
                if month > 12:
                    month = 1
                    year += 1
        return ("%04d-%02d-%02d" % (year, month, day),
                "%02d:%02d" % (hour, minute))
    except Exception:
        return "", ""

def _fast_sports_answer():
    date_key = _today_text()
    if date_key == "bilinmiyor":
        return None
    path = ("/apis/site/v2/sports/soccer/all/scoreboard?dates=" +
            date_key.replace("-", "") + "&limit=8")
    status, raw = https_get("site.api.espn.com", path, 12)
    if status != 200 or not raw:
        return None
    gc.collect()
    data = json.loads(raw)
    raw = None
    matches = []
    for event in data.get("events") or []:
        local_date, local_time = _event_local_date_time(event.get("date", ""))
        if local_date != date_key:
            continue
        competitions = event.get("competitions") or []
        if not competitions:
            continue
        competition = competitions[0]
        home = None
        away = None
        home_score = ""
        away_score = ""
        for competitor in competition.get("competitors") or []:
            team = competitor.get("team") or {}
            name = team.get("shortDisplayName") or team.get("displayName")
            if competitor.get("homeAway") == "home":
                home = name
                home_score = str(competitor.get("score", ""))
            elif competitor.get("homeAway") == "away":
                away = name
                away_score = str(competitor.get("score", ""))
        if not home or not away:
            continue
        status_type = ((competition.get("status") or {}).get("type") or {})
        state = status_type.get("state")
        line = local_time + " " + home + " - " + away
        if state in ("in", "post"):
            line += " " + home_score + "-" + away_score
        matches.append((local_time, line))
    data = None
    gc.collect()
    if not matches:
        return None
    matches.sort()
    return "Bugunun onemli maclari: " + "; ".join(
        item[1] for item in matches[:6]) + "."

def _daily_item(daily, key, index):
    values = daily.get(key) or []
    if index < len(values):
        return values[index]
    return None

def _wind_direction_name(value):
    try:
        names = ("K", "KD", "D", "GD", "G", "GB", "B", "KB")
        return names[int((float(value) + 22.5) // 45) % 8]
    except Exception:
        return ""

def _fast_weather_answer(text):
    if USER_LAT is None or USER_LON is None:
        return None
    path = ("/v1/forecast?latitude=%s&longitude=%s"
            "&current=temperature_2m,relative_humidity_2m,"
            "apparent_temperature,precipitation,rain,snowfall,weather_code,"
            "cloud_cover,surface_pressure,visibility,wind_speed_10m,"
            "wind_direction_10m,wind_gusts_10m"
            "&daily=weather_code,temperature_2m_max,temperature_2m_min,"
            "apparent_temperature_max,apparent_temperature_min,"
            "precipitation_probability_max,uv_index_max,sunrise,sunset"
            "&timezone=auto&forecast_days=3") % (str(USER_LAT), str(USER_LON))
    status, raw = https_get("api.open-meteo.com", path, 10)
    if status != 200 or not raw:
        return None
    data = json.loads(raw)
    daily = data.get("daily") or {}
    place = USER_REGION if USER_REGION else USER_CITY
    if " yarin " in text:
        index = 1
        date_value = _daily_item(daily, "time", index)
        low = _daily_item(daily, "temperature_2m_min", index)
        high = _daily_item(daily, "temperature_2m_max", index)
        feels_low = _daily_item(daily, "apparent_temperature_min", index)
        feels_high = _daily_item(daily, "apparent_temperature_max", index)
        rain_chance = _daily_item(
            daily, "precipitation_probability_max", index)
        uv = _daily_item(daily, "uv_index_max", index)
        condition = _weather_condition(
            _daily_item(daily, "weather_code", index))
        if date_value is None or low is None or high is None:
            return None
        answer = "Yarin %s: %s, en dusuk %.1f C, en yuksek %.1f C" % (
            place, condition, float(low), float(high))
        if feels_low is not None and feels_high is not None:
            answer += ", hissedilen %.1f-%.1f C" % (
                float(feels_low), float(feels_high))
        if rain_chance is not None:
            answer += ". Yagis ihtimali %%%d" % int(float(rain_chance))
        if uv is not None:
            answer += ", UV en fazla %.1f" % float(uv)
        sunrise = _daily_item(daily, "sunrise", index)
        sunset = _daily_item(daily, "sunset", index)
        if sunrise and sunset:
            answer += ". Gun dogumu %s, gun batimi %s" % (
                sunrise[11:16], sunset[11:16])
        return answer + ". Tahmin tarihi " + _display_date(date_value) + "."

    current = data.get("current") or {}
    temp = current.get("temperature_2m")
    feels = current.get("apparent_temperature")
    if temp is None:
        return None
    condition = _weather_condition(current.get("weather_code"))
    answer = "%s: %.1f C" % (place, float(temp))
    if feels is not None:
        answer += ", hissedilen %.1f C" % float(feels)
    if condition:
        answer += ", " + condition
    low = _daily_item(daily, "temperature_2m_min", 0)
    high = _daily_item(daily, "temperature_2m_max", 0)
    if low is not None and high is not None:
        answer += ". Bugun en dusuk %.1f C, en yuksek %.1f C" % (
            float(low), float(high))
    humidity = current.get("relative_humidity_2m")
    if humidity is not None:
        answer += ". Nem %%%d" % int(float(humidity))
    precipitation = current.get("precipitation")
    if precipitation is not None:
        answer += ", yagis %.1f mm" % float(precipitation)
    wind = current.get("wind_speed_10m")
    if wind is not None:
        direction = _wind_direction_name(current.get("wind_direction_10m"))
        answer += ". Ruzgar %s %.1f km/s" % (direction, float(wind))
        gust = current.get("wind_gusts_10m")
        if gust is not None:
            answer += ", hamle %.1f km/s" % float(gust)
    pressure = current.get("surface_pressure")
    if pressure is not None:
        answer += ". Basinc %.0f hPa" % float(pressure)
    cloud = current.get("cloud_cover")
    if cloud is not None:
        answer += ", bulut %%%d" % int(float(cloud))
    visibility = current.get("visibility")
    if visibility is not None:
        answer += ", gorus %.1f km" % (float(visibility) / 1000.0)
    uv = _daily_item(daily, "uv_index_max", 0)
    if uv is not None:
        answer += ". UV en fazla %.1f" % float(uv)
    sunrise = _daily_item(daily, "sunrise", 0)
    sunset = _daily_item(daily, "sunset", 0)
    if sunrise and sunset:
        answer += ", gun dogumu %s, gun batimi %s" % (
            sunrise[11:16], sunset[11:16])
    stamp = current.get("time")
    if stamp:
        answer += ". Veri zamani " + _display_date(stamp[:10]) + " " + stamp[11:16]
    return answer + "."

def _tr_money(value):
    return float(str(value).replace(".", "").replace(",", "."))

def _fast_market_data():
    status, raw = https_get("finans.truncgil.com", "/today.json", 10)
    if status != 200 or not raw:
        return None
    return json.loads(raw)

def _fast_currency_answer(text, data=None):
    wants_usd = " dolar " in text or " usd " in text
    wants_eur = " euro " in text or " avro " in text or " eur " in text
    if not (wants_usd or wants_eur or " kur " in text):
        return None
    if data is None:
        data = _fast_market_data()
    if data is None:
        return None
    parts = []
    for wanted, key, label in (
            (wants_usd or not wants_eur, "USD", "Dolar"),
            (wants_eur or not wants_usd, "EUR", "Euro")):
        rate = data.get(key) or {}
        buying = rate.get("Al\u0131\u015f")
        selling = rate.get("Sat\u0131\u015f")
        if wanted and buying and selling:
            buying = _tr_money(buying)
            selling = _tr_money(selling)
            parts.append("%s alis %.2f, satis %.2f TL" %
                         (label, buying, selling))
    if not parts:
        return None
    stamp = str(data.get("Update_Date", ""))
    return ", ".join(parts) + ". Veri zamani " + stamp + "."

def _fast_gold_answer(text):
    choices = []
    if " ceyrek " in text:
        choices.append(("ceyrek-altin", "Ceyrek altin"))
    elif " yarim " in text:
        choices.append(("yarim-altin", "Yarim altin"))
    elif " tam " in text:
        choices.append(("tam-altin", "Tam altin"))
    elif " gumus " in text:
        choices.append(("gumus", "Gumus"))
    else:
        choices.append(("gram-altin", "Gram altin"))
    data = _fast_market_data()
    if data is None:
        return None
    parts = []
    for key, label in choices:
        rate = data.get(key) or {}
        buying = rate.get("Al\u0131\u015f")
        selling = rate.get("Sat\u0131\u015f")
        if buying and selling:
            parts.append("%s alis %.2f, satis %.2f TL" %
                         (label, _tr_money(buying), _tr_money(selling)))
    if not parts:
        return None
    return ", ".join(parts) + ". Veri zamani " + str(data.get("Update_Date", "")) + "."

def _fast_crypto_answer(text):
    wants_btc = " bitcoin " in text or " btc " in text
    wants_eth = " ethereum " in text or " eth " in text
    if not (wants_btc or wants_eth):
        return None
    ids = []
    if wants_btc:
        ids.append("bitcoin")
    if wants_eth:
        ids.append("ethereum")
    path = ("/api/v3/simple/price?ids=" + ",".join(ids) +
            "&vs_currencies=try&include_last_updated_at=true")
    status, raw = https_get("api.coingecko.com", path, 10)
    if status != 200 or not raw:
        return None
    data = json.loads(raw)
    parts = []
    if wants_btc and (data.get("bitcoin") or {}).get("try") is not None:
        parts.append("Bitcoin %d TL" % int(float(data["bitcoin"]["try"]) + 0.5))
    if wants_eth and (data.get("ethereum") or {}).get("try") is not None:
        parts.append("Ethereum %d TL" % int(float(data["ethereum"]["try"]) + 0.5))
    if not parts:
        return None
    return ", ".join(parts) + ". Kontrol tarihi " + _display_date(_today_text()) + "."

def fast_live_answer(q):
    text = _normalize_question(q)
    answer = None
    try:
        if _question_is_sports(text):
            answer = _fast_sports_answer()
        elif any((" " + hint + " ") in text for hint in (
                "hava", "sicaklik", "sogukluk", "yagmur", "nem",
                "ruzgar", "basinc", "uv", "gorus")):
            answer = _fast_weather_answer(text)
        elif (" bitcoin " in text or " btc " in text or
              " ethereum " in text or " eth " in text):
            answer = _fast_crypto_answer(text)
        elif " altin " in text or " gumus " in text:
            answer = _fast_gold_answer(text)
        elif (" dolar " in text or " usd " in text or " euro " in text or
              " avro " in text or " eur " in text or " kur " in text):
            answer = _fast_currency_answer(text)
    except Exception:
        answer = None
    gc.collect()
    return answer

def ask_question(q, web_search=None, search_context="medium", on_delta=None):
    if web_search is None:
        web_search = question_needs_web(q)
    if web_search:
        sp = WEB_SYSTEM_PROMPT % _today_text()
        tok = WEB_MAX_TOKENS
        q = (q + " Bugunun tarihi " + _today_text() +
             ". Web'de ara ve yalnizca en yeni tarihli bilgiyi kullan.")
        if _question_is_sports(q):
            search_context = "medium"
            q = (q + " Bugun dunyadaki en onemli futbol maclarini ara. "
                 "UEFA, Sampiyonlar Ligi, Avrupa Ligi, Avrupa buyuk ligleri, "
                 "milli maclar ve Super Lig arasindan en fazla 6 mac ver.")
    else:
        extra = LEN_PROFILES[ans_len_idx][2]
        tok = LEN_PROFILES[ans_len_idx][1]
        sp = SYSTEM_PROMPT + " " + extra
    return openai_chat(
        [{"role": "system", "content": sp},
         {"role": "user", "content": q}],
        QA_MODEL, web_search, 75 if web_search else 35, max_tok=tok,
        reasoning="none",
        search_context=search_context, on_delta=on_delta)

def _ask_and_show(q):

    release_answer_buffers()
    gc.collect()
    use_web = question_needs_web(q)
    cached_answer = _live_cache_get(q) if use_web else None
    draw_answer_frame()
    if use_web and cached_answer is None:
        _gpt_wait_start()
    answer = cached_answer
    if answer is None:
        answer = fast_live_answer(q) if use_web else None
    if answer is None:
        if not _app._gpt_wait_active:
            _gpt_wait_start()
        answer, err = ask_question(q, use_web)
    else:
        err = None
    if use_web and (err is not None or _answer_refuses_current(answer)):
        answer = None
        if err is None:
            err = "GUNCEL YANIT ALINAMADI"
    _gpt_wait_stop()
    if err is None and not answer:
        err = "GPT BOS YANIT VERDI"
    if err is None and answer:
        answer = strip_source_disclosures(strip_urls(answer))
    if use_web and err is None and answer:
        _live_cache_put(q, answer)
    gc.collect()
    apply_ans_size(ans_size_idx)
    if err is not None:
        txt = to_screen_text(err)
    else:
        txt = to_screen_text(answer)
    lines = wrap_full(
        txt, (WIDTH - 8) // SIZE_PROFILES[ans_size_idx][2])
    if not lines:
        lines = [""]
    action = show_answer(lines)
    release_answer_buffers()
    return action

def _half_ring(cx, cy, r, color, side):


    x = r; y = 0; err = 0
    while x >= y:
        for (px, py) in ((x, y), (y, x), (-y, x), (-x, y),
                         (-x, -y), (-y, -x), (y, -x), (x, -y)):
            if (side < 0 and px <= 0) or (side > 0 and px >= 0):
                lcd.fill_rect(cx + px, cy + py, 1, 1, color)
        y += 1
        if err <= 0:
            err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1

def _draw_pill(x, y, w, h, fill_col, border_col, txt, txt_col):


    r = h // 2
    lcd.fill_rect(x + r, y, w - 2 * r, h, fill_col)
    _fast_disc(x + r, y + r, r, fill_col)
    _fast_disc(x + w - r, y + r, r, fill_col)
    _half_ring(x + r, y + r, r, border_col, -1)
    _half_ring(x + w - r, y + r, r, border_col, 1)
    lcd.hline(x + r, y, w - 2 * r, border_col)
    lcd.hline(x + r, y + h - 1, w - 2 * r, border_col)
    tx = x + (w - len(txt) * 6) // 2
    ty = y + (h - 7) // 2
    lcd.text(txt, tx, ty, txt_col, 1)

def _sor_pill_layout():


    pills = []
    x = _SOR_MARGIN_X
    y = _SOR_PILL_Y0
    max_x = WIDTH - _SOR_MARGIN_X
    for label, question in PRESET_Q:
        pw = len(label) * 6 + _SOR_PILL_PAD * 2
        if x != _SOR_MARGIN_X and x + pw > max_x:
            x = _SOR_MARGIN_X
            y += _SOR_PILL_H + _SOR_GAP_Y
        pills.append((x, y, pw, _SOR_PILL_H, label, question))
        x += pw + _SOR_GAP_X
    return pills

# Kose saati IKI SEKMEDE DE ayni yerde. Mevcut duzeni hic degistirmeyen
# tek ortak bosluk burasi:
#   klavye     : 'z' satirinin solu -- tuslar x=48'den basliyor, GERI
#                tusu sagdaki bosluga oturuyor, sol 48 piksel bos.
#   hazir soru : son kutucuk satiri y=138'de bitiyor, alt serit 214'te
#                basliyor; arasi tamamen bos.
# Hazir soru ekraninda GERI alt ortada (148, 214) oldugu icin saat
# gercekten onun sol ustune dusuyor.
_SAAT_X = 9
_SAAT_Y = 187


def _sor_tabs_draw(active):


    labels = ["GPT", "HAZIR SORU"]
    bw = WIDTH // 2 - 6
    for slot in range(2):
        idx = 1 - slot
        bx = 3 + slot * (WIDTH // 2)
        on = (idx == active)
        bg = FG if on else TAB_UNSEL
        fg = BG if on else WHITE
        _draw_round_rect(bx, _SOR_TABS_Y0, bw, _SOR_TABS_H, 9, bg, GRAY)
        lbl = labels[idx]
        lcd.text(lbl, bx + (bw - len(lbl) * 12) // 2,
                  _SOR_TABS_Y0 + (_SOR_TABS_H - 14) // 2, fg, 2)

def _sor_hit_tab(x, y):


    if y < _SOR_TABS_Y0 or y > _SOR_TABS_Y0 + _SOR_TABS_H:
        return None
    return 1 if x < WIDTH // 2 else 0

def _sor_hazir_draw():
    lcd.fill_rect(0, 0, WIDTH, HEIGHT, BG)
    _sor_tabs_draw(1)
    for (x, y, w, h, label, question) in _sor_pill_layout():
        _draw_pill(x, y, w, h, DARKGRAY, GRAY, label, WHITE)
    lcd.fill_rect(0, _SOR_HAZIR_GERI_Y, WIDTH, _SOR_HAZIR_GERI_H, DARKGRAY)
    lcd.hline(0, _SOR_HAZIR_GERI_Y, WIDTH, GRAY)
    lcd.text("GERI", (WIDTH - 24) // 2, _SOR_HAZIR_GERI_Y + 9, WHITE, 1)
    _mini_saat(True, _SAAT_X, _SAAT_Y)

def _sor_in_pos(idx):
    return _SOR_IN_X + (idx % IN_CPL) * IN_CW, _SOR_IN_Y + (idx // IN_CPL) * IN_CH

def _sor_in_char_at(idx, ch):
    x, y = _sor_in_pos(idx)
    if y > KB_TOP - 12:
        return
    lcd.text(ch, x, y, FG, 1)

def _sor_in_erase_at(idx):
    x, y = _sor_in_pos(idx)
    if y > KB_TOP - 12:
        return
    lcd.fill_rect(x, y, IN_CW, IN_CH, BG)

def _sor_in_draw_all(text):
    for i in range(len(text)):
        _sor_in_char_at(i, text[i])

def _sor_kb_build(mode):


    keys = _kb_build(mode)
    keys.append({"label": "GERI", "x": _SOR_KB_GERI_X, "y": _SOR_KB_GERI_Y,
                 "w": _SOR_KB_GERI_W, "h": KEY_H, "kind": "geri"})
    return keys

def _run_sor_keyboard():


    text = ""
    mode = "low"
    keys = _sor_kb_build(mode)
    lcd.fill_rect(0, 0, WIDTH, HEIGHT, BG)
    _sor_tabs_draw(0)
    _kb_draw(keys)
    _sor_in_draw_all(text)
    _mini_saat(True, _SAAT_X, _SAAT_Y)
    last = 0
    while True:
        p = touch.read_fast()
        if p is None:
            _mini_saat(x=_SAAT_X, y=_SAAT_Y)
            time.sleep_ms(20)
            continue
        now = time.ticks_ms()
        if time.ticks_diff(now, last) < 90:
            continue
        last = now
        x, y = p
        tab = _sor_hit_tab(x, y)
        if tab is not None:
            if tab == 1:
                _wait_touch_release()
                return "__switch__"
            continue
        if y < _SOR_CONTENT_Y0:
            continue
        k = None
        for kk in keys:
            if kk["x"] <= x <= kk["x"] + kk["w"] and kk["y"] <= y <= kk["y"] + kk["h"]:
                k = kk
                break
        if k is None:
            continue
        _kb_key_draw(k, True)
        time.sleep_ms(30)
        _kb_key_draw(k, False)
        kind = k["kind"]
        if kind == "geri":
            _wait_touch_release()
            return None
        elif kind == "char":
            if len(text) < 64:
                idx = len(text)
                text += k["val"]
                _sor_in_char_at(idx, k["val"])
        elif kind == "space":
            if len(text) < 64:
                text += " "
        elif kind == "back":
            if text:
                idx = len(text) - 1
                text = text[:-1]
                _sor_in_erase_at(idx)
        elif kind == "case":
            mode = "up" if mode == "low" else "low"
            keys = _sor_kb_build(mode)
            _kb_draw(keys)
        elif kind == "sym":
            mode = "sym"
            keys = _sor_kb_build(mode)
            _kb_draw(keys)
        elif kind == "toletters":
            mode = "low"
            keys = _sor_kb_build(mode)
            _kb_draw(keys)
        elif kind == "send":
            return text

def run_sor():

    view = 1
    while True:
        if view == 0:
            q = _run_sor_keyboard()
            if q is None:
                return
            if q == "__switch__":
                view = 1
                continue
            q = q.strip()
            if q:
                act = _ask_and_show(q)
                if act == "back":
                    view = 1
                    continue
            continue

        _sor_hazir_draw()
        _wait_touch_release()
        last = 0
        next_view = None
        while next_view is None:
            p = touch.read_fast()
            if p is None:
                _mini_saat(x=_SAAT_X, y=_SAAT_Y)
                time.sleep_ms(20)
                continue
            now = time.ticks_ms()
            if time.ticks_diff(now, last) < TOUCH_DEBOUNCE_MS:
                continue
            last = now
            x, y = p
            if y >= _SOR_HAZIR_GERI_Y:
                _wait_touch_release()
                return
            tab = _sor_hit_tab(x, y)
            if tab is not None:
                if tab == 0:
                    _wait_touch_release()
                    next_view = 0
                continue
            for (px, py, pw, ph, label, question) in _sor_pill_layout():
                if px <= x <= px + pw and py <= y <= py + ph:
                    _wait_touch_release()
                    q_text = question() if callable(question) else question
                    _ask_and_show(q_text)
                    next_view = 1
                    break
        view = next_view

def _open_sor_impl():
    if is_online():
        run_sor()
    else:
        show_status_screen("ONCE WIFI BAGLAN", AMBER)
        time.sleep_ms(1200)
    draw_static()
