import gc
import os

gc.collect()

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
    raise
