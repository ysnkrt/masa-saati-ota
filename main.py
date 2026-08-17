import gc
import os

try:
    import machine
except Exception:
    machine = None

_OTA_PENDING = "ota_pending.txt"
_OTA_BOOTING = "ota_booting.txt"
_OTA_FILES = (
    "main.py", "clock_app.mpy", "gpt_stream.py", "sor_feature.py",
    "ota_feature.py", "ota_release.txt", "ca_roots.der",
)

# Acilis hata sayaci. Uygulama calismaya baslamadan ONCE artirilir ve
# clock_app bir sure sorunsuz calisinca siler. Boylece hem istisna atan
# hem de sessizce kilitlenen kod yakalanir: kilitlenen kod sayaci asla
# silemez, kullanici cihazi kapatip actikca sayac artar ve sinira gelince
# uygulama hic baslatilmaz -- REPL acik kalir, USB'den mudahale edilir.
_BOOT_FAIL_FILE = "acilis_hata.txt"
_BOOT_FAIL_LIMIT = 3


def _exists(path):
    try:
        os.stat(path)
        return True
    except Exception:
        return False


def _remove(path):
    try:
        os.remove(path)
    except Exception:
        pass


def _boot_fail_count():
    try:
        f = open(_BOOT_FAIL_FILE)
        value = f.read().strip()
        f.close()
        return int(value)
    except Exception:
        return 0


def _boot_fail_bump(count):
    try:
        f = open(_BOOT_FAIL_FILE, "w")
        f.write(str(count))
        f.close()
    except Exception:
        pass


def _restore_ota_backup():
    restored = False
    for name in _OTA_FILES:
        backup = ".bak_" + name
        if _exists(backup):
            _remove(name)
            try:
                os.rename(backup, name)
                restored = True
            except Exception:
                pass
        _remove(".ota_" + name)
    _remove(_OTA_PENDING)
    _remove(_OTA_BOOTING)
    return restored


def _prepare_ota_boot():
    if not _exists(_OTA_PENDING):
        return False
    if _exists(_OTA_BOOTING):
        _restore_ota_backup()
        return False
    try:
        f = open(_OTA_BOOTING, "w")
        f.write("1")
        f.close()
        return True
    except Exception:
        _restore_ota_backup()
        return False


gc.collect()

_fails = _boot_fail_count()
if _fails >= _BOOT_FAIL_LIMIT:
    # Guvenli mod: uygulamayi hic baslatma. Bir OTA denemesi yarim
    # kaldiysa once onu geri al, sonra REPL'e dus.
    if _exists(_OTA_PENDING) or _exists(_OTA_BOOTING):
        _restore_ota_backup()
    print()
    print("=" * 46)
    print(" GUVENLI MOD - acilis %d kez basarisiz oldu." % _fails)
    print(" Uygulama baslatilmadi, REPL kullanilabilir.")
    print(" Hata kayitlari: hatalar.txt / last_error.txt")
    print(" Normale donmek icin: os.remove('%s')" % _BOOT_FAIL_FILE)
    print("=" * 46)
else:
    _boot_fail_bump(_fails + 1)
    _ota_trial_boot = _prepare_ota_boot()

    try:
        # clock_app onceden derlenmis .mpy olarak geliyor; cihazda
        # derleyici yok. clock_app.py bulunursa .mpy'yi golgeler ve saat
        # hic acilmaz, bu yuzden siliniyor.
        try:
            os.stat("clock_app.mpy")
            try:
                os.stat("clock_app.py")
                os.remove("clock_app.py")
            except Exception:
                pass
        except Exception:
            pass
        for _name in ("gpt_stream", "sor_feature", "ota_feature"):
            try:
                os.stat(_name + ".py")
                os.remove(_name + ".mpy")
            except Exception:
                pass
        import clock_app
        clock_app.run_clock()
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        try:
            f = open("last_error.txt", "w")
            f.write(repr(exc) + "\n")
            f.close()
        except Exception:
            pass
        if _ota_trial_boot:
            _restore_ota_backup()
            if machine is not None:
                try:
                    machine.reset()
                except Exception:
                    pass
        raise
