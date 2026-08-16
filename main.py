import gc
import os

try:
    import machine
except Exception:
    machine = None

_OTA_PENDING = "ota_pending.txt"
_OTA_BOOTING = "ota_booting.txt"
_OTA_FILES = (
    "main.py", "clock_app.py", "gpt_stream.py", "sor_feature.py",
    "ota_feature.py", "ota_release.txt",
)


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
_ota_trial_boot = _prepare_ota_boot()

try:
    for _name in ("clock_app", "gpt_stream", "sor_feature", "ota_feature"):
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
