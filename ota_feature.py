_ALLOWED_FILES = (
    "main.py", "clock_app.py", "gpt_stream.py", "sor_feature.py",
    "ota_feature.py", "ota_release.txt",
)
_OTA_URL_FILE = "ota_url.txt"


def _bind(app):
    here = globals()
    for name, value in app.__dict__.items():
        if name not in here:
            here[name] = value


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
    try:
        f = open(_OTA_URL_FILE)
        value = f.read().strip()
        f.close()
        if value.startswith("https://"):
            return value
    except Exception:
        pass
    return OTA_MANIFEST_URL


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
        if not files or "clock_app.py" not in seen:
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


def _download(url, temp_path, expected_sha):
    if hashlib is None or socket is None or ssl is None:
        return False, "AG VEYA SHA MODULU YOK"
    host, path = _parse_url(url)
    if not host:
        return False, "DOSYA ADRESI GECERSIZ"
    raw = None
    secure = None
    out = None
    try:
        try:
            os.remove(temp_path)
        except Exception:
            pass
        addr = socket.getaddrinfo(host, 443)[0][-1]
        raw = socket.socket()
        try:
            raw.settimeout(30)
        except Exception:
            pass
        raw.connect(addr)
        try:
            secure = ssl.wrap_socket(raw, server_hostname=host)
        except TypeError:
            secure = ssl.wrap_socket(raw)
        request = ("GET " + path + " HTTP/1.1\r\nHost: " + host +
                   "\r\nUser-Agent: masa-saati/" + APP_VERSION +
                   "\r\nAccept: application/octet-stream\r\n"
                   "Connection: close\r\n\r\n")
        secure.write(request.encode("utf-8"))
        status_line = secure.readline()
        try:
            status = int(status_line.split(b" ")[1])
        except Exception:
            status = 0
        chunked = False
        expected_size = 0
        while True:
            line = secure.readline()
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


def _preserve_api_key(temp_path):
    source = None
    target = None
    ready = temp_path + ".ready"
    try:
        source = open(temp_path, "r")
        target = open(ready, "w")
        replaced = False
        for line in source:
            if line.startswith("OPENAI_API_KEY ="):
                target.write("OPENAI_API_KEY = " +
                             repr(OPENAI_API_KEY.strip()) + "\n")
                replaced = True
            else:
                target.write(line)
        source.close()
        source = None
        target.close()
        target = None
        if not replaced:
            return False, "API ANAHTARI KORUNAMADI"
        os.remove(temp_path)
        os.rename(ready, temp_path)
        return True, None
    except Exception as exc:
        return False, "API ANAHTARI: " + str(exc)
    finally:
        for handle in (source, target):
            if handle is not None:
                try:
                    handle.close()
                except Exception:
                    pass


def _install(files):
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
        for _name, backup in installed:
            if backup:
                try:
                    os.remove(backup)
                except Exception:
                    pass
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
    for index, item in enumerate(files):
        show_status_screen("INDIRILIYOR %d/%d" % (index + 1, len(files)),
                           TITLE_COL)
        temp = ".ota_" + item["path"]
        ok, err = _download(item["url"], temp, item["sha256"])
        if not ok:
            show_status_screen(to_screen_text(err)[:48], RED)
            time.sleep_ms(2200)
            return
        if item["path"] == "clock_app.py":
            ok, err = _preserve_api_key(temp)
            if not ok:
                show_status_screen(to_screen_text(err)[:48], RED)
                time.sleep_ms(2200)
                return
    show_status_screen("DOGRULANDI, KURULUYOR", GREEN)
    ok, err = _install(files)
    if not ok:
        show_status_screen(to_screen_text(err)[:48], RED)
        time.sleep_ms(2200)
        return
    show_status_screen("TAMAM, YENIDEN BASLIYOR", GREEN)
    time.sleep_ms(1200)
    if machine_reset is not None:
        machine_reset()


def run(app):
    _bind(app)
    return run_ota_update()
