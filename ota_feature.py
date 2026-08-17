_ALLOWED_FILES = (
    "main.py", "clock_app.mpy", "gpt_stream.py", "sor_feature.py",
    "ota_feature.py", "ota_release.txt", "ca_roots.der",
)
_OTA_URL_FILE = "ota_url.txt"

# Bu modul clock_app'in isim alanindan calisir. Eskiden tum isimler
# sessizce kopyalaniyordu; neye bagimli oldugu hicbir yerde yazmiyordu ve
# eksik bir isim ancak calisma aninda NameError olarak ortaya cikiyordu.
# Asagidaki liste bagimliliklari acik hale getirir ve eksigi hemen bildirir.
_REQUIRED = (
    "lcd", "touch", "time", "os", "gc", "json", "math", "socket", "ssl",
    "hashlib", "show_status_screen", "to_screen_text", "is_online",
    "release_answer_buffers", "_wait_touch_release", "_watchdog_touch",
    "tls_connect", "https_get", "log_error", "machine_reset",
    "OTA_RELEASE_FILE", "OTA_MANIFEST_URL", "OTA_MAX_BYTES", "APP_VERSION",
    "WIDTH", "BG", "FG", "GREEN", "RED", "GRAY", "DARKGRAY", "WHITE",
    "BLACK", "CYAN", "AMBER", "TITLE_COL", "_PI",
)


def _bind(app):
    here = globals()
    for name, value in app.__dict__.items():
        if name not in here:
            here[name] = value
    missing = [n for n in _REQUIRED if n not in here]
    if missing:
        raise RuntimeError("ota_feature eksik bagimlilik: " + ", ".join(missing))


def _parse_url(url):
    prefix = "https://"
    if not url.startswith(prefix):
        return None, None
    rest = url[len(prefix):]
    slash = rest.find("/")
    if slash < 0:
        return rest, "/"
    return rest[:slash], rest[slash:]


def _digest_hex(hasher):
    return "".join("%02x" % b for b in hasher.digest())


def _local_release():
    try:
        f = open(OTA_RELEASE_FILE)
        value = f.read().strip()
        f.close()
        return value
    except Exception:
        return ""


def _manifest_url():
    value = OTA_MANIFEST_URL
    try:
        f = open(_OTA_URL_FILE)
        configured = f.read().strip()
        f.close()
        if configured.startswith("https://"):
            value = configured
    except Exception:
        pass
    separator = "&" if "?" in value else "?"
    return value + separator + "cb=" + str(time.ticks_ms())


def _manifest():
    host, path = _parse_url(_manifest_url())
    if not host:
        return None, "OTA ADRESI GECERSIZ"
    try:
        status, text = https_get(host, path, 20)
        if status != 200 or not text:
            return None, "OTA SUNUCU KODU " + str(status)
        data = json.loads(text)
        version = str(data.get("version", "")).strip()
        release_id = str(data.get("release_id", "")).strip()
        raw_files = data.get("files", [])
        notes = data.get("notes", [])
        if not version or not release_id or not isinstance(raw_files, list):
            return None, "OTA BILGISI EKSIK"
        files = []
        seen = {}
        for item in raw_files:
            name = str(item.get("path", "")).strip()
            url = str(item.get("url", "")).strip()
            digest = str(item.get("sha256", "")).strip().lower()
            if (name not in _ALLOWED_FILES or name in seen or
                    not url.startswith("https://") or len(digest) != 64):
                return None, "OTA DOSYA BILGISI HATALI"
            seen[name] = True
            files.append({"path": name, "url": url, "sha256": digest})
        if not files or "clock_app.mpy" not in seen:
            return None, "OTA DOSYALARI EKSIK"
        if not isinstance(notes, list):
            notes = [str(notes)]
        return {"version": version, "release_id": release_id,
                "files": files, "notes": notes[:3]}, None
    except Exception as exc:
        return None, "OTA BAGLANTI: " + str(exc)
    finally:
        gc.collect()


def has_update(app):
    _bind(app)
    manifest, err = _manifest()
    return bool(err is None and manifest is not None and
                manifest["release_id"] != _local_release())


def _confirm(manifest):
    lcd.fill(BG)
    lcd.text("YAZILIM GUNCELLEMESI", 34, 14, TITLE_COL, 2)
    version = "SURUM  v" + manifest["version"]
    lcd.text(version, (WIDTH - len(version) * 6) // 2, 51, GREEN, 1)
    lcd.hline(24, 72, WIDTH - 48, DARKGRAY)
    lcd.text("YENILIKLER", 127, 84, TITLE_COL, 1)
    notes = manifest.get("notes") or ["Yeni kod paketi"]
    y = 106
    for note in notes:
        line = "- " + to_screen_text(str(note))
        if len(line) > 50:
            line = line[:47] + "..."
        lcd.text(line, 10, y, FG, 1)
        y += 16
    lcd.fill_rect(0, 198, 158, 42, DARKGRAY)
    lcd.rect(0, 198, 158, 42, GRAY)
    lcd.text("IPTAL", 64, 215, WHITE, 1)
    lcd.fill_rect(162, 198, 158, 42, GREEN)
    lcd.rect(162, 198, 158, 42, GRAY)
    lcd.text("GUNCELLE", 215, 215, BLACK, 1)
    _wait_touch_release()
    while True:
        p = touch.read_fast()
        if p is None:
            time.sleep_ms(20)
            continue
        x, y = p
        if y >= 198:
            _wait_touch_release()
            return x >= WIDTH // 2


_OTA_ANIM_FRAME = 0
_OTA_ANIM_LAST = 0


def _ota_ring_segment(index, color):
    cx = WIDTH // 2
    cy = 108
    radius = 55
    angle = index * 2.0 * _PI / 36.0
    inner = radius - (9 if index % 3 == 0 else 5)
    x0 = cx + int(inner * math.sin(angle))
    y0 = cy - int(inner * math.cos(angle))
    x1 = cx + int(radius * math.sin(angle))
    y1 = cy - int(radius * math.cos(angle))
    lcd.line(x0, y0, x1, y1, color)


def _ota_anim_tick(force=False):
    global _OTA_ANIM_FRAME, _OTA_ANIM_LAST
    _watchdog_touch()
    now = time.ticks_ms()
    if (not force and
            time.ticks_diff(now, _OTA_ANIM_LAST) < 70):
        return
    _OTA_ANIM_LAST = now
    _ota_ring_segment((_OTA_ANIM_FRAME - 5) % 36, DARKGRAY)
    colors = (CYAN, TITLE_COL, TITLE_COL, FG, DARKGRAY)
    for distance in range(4, -1, -1):
        _ota_ring_segment((_OTA_ANIM_FRAME - distance) % 36,
                          colors[distance])
    bar_x = 70
    inner_w = WIDTH - 144
    segment_w = 28
    travel = inner_w - segment_w
    phase = (_OTA_ANIM_FRAME * 7) % max(1, travel * 2)
    pos = phase if phase <= travel else travel * 2 - phase
    lcd.fill_rect(bar_x + 2, 222, inner_w, 2, DARKGRAY)
    lcd.fill_rect(bar_x + 2 + pos, 222, segment_w, 2, TITLE_COL)
    _OTA_ANIM_FRAME = (_OTA_ANIM_FRAME + 1) % 36


def _ota_anim_start():
    global _OTA_ANIM_FRAME, _OTA_ANIM_LAST
    _OTA_ANIM_FRAME = 0
    _OTA_ANIM_LAST = 0
    lcd.fill(BG)
    for index in range(36):
        _ota_ring_segment(index, DARKGRAY)
    lcd.rect(70, 220, WIDTH - 140, 6, DARKGRAY)
    _ota_anim_tick(True)


def _ota_anim_success():
    lcd.fill(BG)
    for offset in range(4):
        lcd.line(112, 121 + offset, 145, 151 + offset, GREEN)
        lcd.line(145, 151 + offset, 211, 84 + offset, GREEN)


def _download(url, temp_path, expected_sha, progress=None):
    if hashlib is None or socket is None or ssl is None:
        return False, "AG VEYA SHA MODULU YOK"
    host, path = _parse_url(url)
    if not host:
        return False, "DOSYA ADRESI GECERSIZ"
    raw = None
    secure = None
    out = None
    try:
        if progress is not None:
            progress()
        try:
            os.remove(temp_path)
        except Exception:
            pass
        # Dogrulanmis TLS. Eskiden sertifika hic denetlenmiyordu; SHA-256
        # kontrolu de koruma saglamiyordu, cunku beklenen ozetler ayni
        # dogrulanmamis kanaldan gelen manifest'in icindeydi. Araya giren
        # biri kendi manifest'ini ve ona uyan dosyalari sunup cihaza
        # istedigi kodu calistirabiliyordu.
        secure, raw = tls_connect(host, 30)
        if progress is not None:
            progress()
        request = ("GET " + path + " HTTP/1.1\r\nHost: " + host +
                   "\r\nUser-Agent: masa-saati/" + APP_VERSION +
                   "\r\nAccept: application/octet-stream\r\n"
                   "Connection: close\r\n\r\n")
        secure.write(request.encode("utf-8"))
        if progress is not None:
            progress()
        status_line = secure.readline()
        try:
            status = int(status_line.split(b" ")[1])
        except Exception:
            status = 0
        chunked = False
        expected_size = 0
        while True:
            line = secure.readline()
            if progress is not None:
                progress()
            if not line or line in (b"\r\n", b"\n"):
                break
            low = line.lower()
            if low.startswith(b"transfer-encoding:") and b"chunked" in low:
                chunked = True
            elif low.startswith(b"content-length:"):
                try:
                    expected_size = int(line.split(b":", 1)[1].strip())
                except Exception:
                    expected_size = 0
        if status != 200:
            return False, "DOSYA SUNUCU KODU " + str(status)
        if expected_size > OTA_MAX_BYTES:
            return False, "DOSYA COK BUYUK"
        out = open(temp_path, "wb")
        hasher = hashlib.sha256()
        done = 0
        if chunked:
            while True:
                header = secure.readline()
                if not header:
                    raise OSError("chunk basligi yok")
                size = int(header.split(b";", 1)[0].strip(), 16)
                if size == 0:
                    break
                remaining = size
                while remaining:
                    block = secure.read(min(512, remaining))
                    if not block:
                        raise OSError("dosya yarim")
                    out.write(block)
                    hasher.update(block)
                    done += len(block)
                    remaining -= len(block)
                    if progress is not None:
                        progress()
                    if done > OTA_MAX_BYTES:
                        raise OSError("dosya cok buyuk")
                secure.read(2)
        else:
            while True:
                block = secure.read(512)
                if not block:
                    break
                out.write(block)
                hasher.update(block)
                done += len(block)
                if progress is not None:
                    progress()
                if done > OTA_MAX_BYTES:
                    raise OSError("dosya cok buyuk")
        out.close()
        out = None
        if expected_size and done != expected_size:
            return False, "DOSYA YARIM"
        if _digest_hex(hasher) != expected_sha:
            return False, "SHA256 HATALI"
        return True, None
    except Exception as exc:
        return False, "INDIRME: " + str(exc)
    finally:
        if out is not None:
            try:
                out.close()
            except Exception:
                pass
        if secure is not None:
            try:
                secure.close()
            except Exception:
                pass
        elif raw is not None:
            try:
                raw.close()
            except Exception:
                pass
        gc.collect()


# _preserve_api_key kaldirildi. Anahtar artik kaynak kodda degil, cihazdaki
# openai_key.txt dosyasinda duruyor; OTA o dosyaya dokunmadigi icin anahtari
# indirilen kaynaga yeniden enjekte etmeye gerek yok. Eski yontem ayrica
# kirilgandi: yeni surumde "OPENAI_API_KEY =" satirinin bicimi degisirse
# guncelleme komple iptal oluyordu.


def _install(files, release_id):
    installed = []
    try:
        for item in files:
            name = item["path"]
            temp = ".ota_" + name
            backup = ".bak_" + name
            try:
                os.remove(backup)
            except Exception:
                pass
            try:
                os.rename(name, backup)
            except Exception:
                backup = None
            try:
                os.rename(temp, name)
            except Exception:
                if backup:
                    try:
                        os.rename(backup, name)
                    except Exception:
                        pass
                raise
            installed.append((name, backup))
        try:
            os.remove("ota_booting.txt")
        except Exception:
            pass
        marker = open("ota_pending.txt", "w")
        marker.write(str(release_id))
        marker.close()
        return True, None
    except Exception as exc:
        for name, backup in reversed(installed):
            try:
                os.remove(name)
            except Exception:
                pass
            if backup:
                try:
                    os.rename(backup, name)
                except Exception:
                    pass
        return False, "KURULUM: " + str(exc)


def run_ota_update():
    if not is_online():
        show_status_screen("OTA ICIN WIFI GEREKLI", AMBER)
        time.sleep_ms(1400)
        return
    show_status_screen("GUNCELLEME KONTROL EDILIYOR", TITLE_COL)
    release_answer_buffers()
    gc.collect()
    manifest, err = _manifest()
    if err is not None:
        show_status_screen(to_screen_text(err)[:48], RED)
        time.sleep_ms(2000)
        return
    if manifest["release_id"] == _local_release():
        show_status_screen("KOD GUNCEL: v" + APP_VERSION, GREEN)
        time.sleep_ms(1400)
        return
    if not _confirm(manifest):
        return
    files = manifest["files"]
    _ota_anim_start()
    for item in files:
        temp = ".ota_" + item["path"]
        ok, err = _download(item["url"], temp, item["sha256"],
                            _ota_anim_tick)
        if not ok:
            show_status_screen(to_screen_text(err)[:48], RED)
            time.sleep_ms(2200)
            return
    _ota_anim_tick(True)
    ok, err = _install(files, manifest["release_id"])
    if not ok:
        show_status_screen(to_screen_text(err)[:48], RED)
        time.sleep_ms(2200)
        return
    _ota_anim_success()
    time.sleep_ms(700)
    if machine_reset is not None:
        machine_reset()


def run(app):
    _bind(app)
    return run_ota_update()
