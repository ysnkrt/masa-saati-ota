import gc
import time

try:
    import json
except Exception:
    import ujson as json
try:
    import socket
    import ssl
except Exception:
    socket = None
    ssl = None
try:
    import select
except Exception:
    try:
        import uselect as select
    except Exception:
        select = None


def _find(data, needle):
    limit = len(data) - len(needle)
    pos = 0
    while pos <= limit:
        if data[pos:pos + len(needle)] == needle:
            return pos
        pos += 1
    return -1


def _text(data):
    if isinstance(data, bytearray):
        data = bytes(data)
    try:
        return data.decode("utf-8")
    except Exception:
        return data.decode()


class _SocketReader:
    def __init__(self, stream, timeout, wait):
        self.stream = stream
        self.timeout = timeout * 1000
        self.started = time.ticks_ms()
        self.wait = wait
        self.buf = bytearray()
        self.pos = 0
        self.eof = False
        self.poller = None
        if select is not None:
            try:
                self.poller = select.poll()
                self.poller.register(stream, select.POLLIN)
            except Exception:
                self.poller = None

    def _compact(self):
        if self.pos >= len(self.buf):
            self.buf = bytearray()
            self.pos = 0
        elif self.pos >= 512:
            self.buf = self.buf[self.pos:]
            self.pos = 0

    def _fill(self):
        if self.eof:
            return False
        errors = 0
        while time.ticks_diff(time.ticks_ms(), self.started) < self.timeout:
            if self.poller is not None:
                try:
                    ready = self.poller.poll(40)
                except Exception:
                    self.poller = None
                    ready = None
                if self.poller is not None and not ready:
                    if self.wait:
                        self.wait()
                    continue
            try:
                data = self.stream.read(512)
            except Exception:
                errors += 1
                if self.poller is not None and errors < 200:
                    if self.wait:
                        self.wait()
                    time.sleep_ms(10)
                    continue
                raise
            if data is None:
                if self.wait:
                    self.wait()
                time.sleep_ms(10)
                continue
            if not data:
                self.eof = True
                return False
            self._compact()
            self.buf.extend(data)
            if self.wait:
                self.wait()
            return True
        self.eof = True
        return False

    def read(self, maximum=512):
        while self.pos >= len(self.buf):
            self._compact()
            if not self._fill():
                return b""
        count = min(maximum, len(self.buf) - self.pos)
        out = bytes(self.buf[self.pos:self.pos + count])
        self.pos += count
        return out

    def exact(self, count):
        out = bytearray()
        while len(out) < count:
            part = self.read(count - len(out))
            if not part:
                break
            out.extend(part)
        return bytes(out)

    def line(self, limit=2048):
        out = bytearray()
        cut = False
        while True:
            while self.pos < len(self.buf):
                value = self.buf[self.pos]
                self.pos += 1
                if value == 10:
                    if out and out[-1] == 13:
                        out = out[:-1]
                    return bytes(out), cut
                if len(out) < limit:
                    out.append(value)
                else:
                    cut = True
            self._compact()
            if not self._fill():
                return bytes(out), cut


class _Body:
    def __init__(self, reader, chunked, length):
        self.reader = reader
        self.chunked = chunked
        self.remaining = length
        self.chunk_left = 0
        self.done = False

    def read(self, maximum=512):
        if self.done:
            return b""
        if not self.chunked:
            if self.remaining == 0:
                self.done = True
                return b""
            count = maximum if self.remaining < 0 else min(maximum, self.remaining)
            data = self.reader.read(count)
            if not data:
                self.done = True
                return b""
            if self.remaining > 0:
                self.remaining -= len(data)
            return data
        while self.chunk_left == 0:
            line, _cut = self.reader.line(64)
            if not line and self.reader.eof:
                self.done = True
                return b""
            if not line:
                continue
            try:
                self.chunk_left = int(line.split(b";", 1)[0], 16)
            except Exception:
                self.done = True
                return b""
            if self.chunk_left == 0:
                self.done = True
                return b""
        data = self.reader.exact(min(maximum, self.chunk_left))
        if not data:
            self.done = True
            return b""
        self.chunk_left -= len(data)
        if self.chunk_left == 0:
            self.reader.exact(2)
        return data


class _Lines:
    def __init__(self, body):
        self.body = body
        self.pending = bytearray()

    def line(self, limit=6144):
        out = bytearray()
        cut = False
        while True:
            pos = _find(self.pending, b"\n")
            if pos >= 0:
                take = min(pos, max(0, limit - len(out)))
                if take:
                    out.extend(self.pending[:take])
                cut = cut or pos > take
                self.pending = self.pending[pos + 1:]
                if out and out[-1] == 13:
                    out = out[:-1]
                return bytes(out), cut
            if self.pending:
                take = min(len(self.pending), max(0, limit - len(out)))
                if take:
                    out.extend(self.pending[:take])
                cut = cut or len(self.pending) > take
                self.pending = bytearray()
            part = self.body.read(256)
            if not part:
                return bytes(out), cut
            self.pending.extend(part)


def post(host, path, key, body_text, timeout=45, on_delta=None, wait=None,
         tls_connect=None):
    """tls_connect: clock_app.tls_connect -- dogrulanmis TLS baglantisi kurar.

    Bu modul bagimsiz oldugu icin kok sertifikalara erisemez; baglantiyi
    disaridan almak zorunda. Verilmezse baglanti kurulmaz (kapali tarafa
    duser), cunku dogrulamasiz baglanti API anahtarini riske atar.
    """
    body = body_text.encode("utf-8")
    sock = None
    secure = None
    parts = []
    error = None
    if tls_connect is None:
        return 0, None, "GUVENLI BAGLANTI SAGLANAMADI"
    try:
        gc.collect()
        # Dogrulanmis TLS: API anahtari Authorization basliginda gidiyor,
        # dogrulanmamis bir baglantida araya giren biri anahtari calabilirdi.
        secure, sock = tls_connect(host, timeout)
        request = (
            "POST " + path + " HTTP/1.1\r\nHost: " + host +
            "\r\nAuthorization: Bearer " + key +
            "\r\nContent-Type: application/json\r\nAccept: text/event-stream"
            "\r\nContent-Length: " + str(len(body)) +
            "\r\nConnection: close\r\n\r\n")
        secure.write(request.encode("utf-8"))
        secure.write(body)
        body = None
        reader = _SocketReader(secure, timeout, wait)
        status_line, _cut = reader.line(256)
        try:
            status = int(status_line.split(b" ")[1])
        except Exception:
            status = 0
        chunked = False
        length = -1
        while True:
            line, _cut = reader.line(512)
            if not line:
                break
            lower = line.lower()
            if lower.startswith(b"transfer-encoding:"):
                chunked = b"chunked" in lower
            elif lower.startswith(b"content-length:"):
                try:
                    length = int(line.split(b":", 1)[1].strip())
                except Exception:
                    length = -1
        response = _Body(reader, chunked, length)
        lines = _Lines(response)
        if status != 200:
            raw = bytearray()
            while len(raw) < 4096:
                block = response.read(min(512, 4096 - len(raw)))
                if not block:
                    break
                raw.extend(block)
            try:
                error = json.loads(_text(raw)).get("error", {}).get("message")
            except Exception:
                pass
            return status, None, error
        event_name = ""
        accepted = (
            "response.output_text.delta", "response.output_text.done",
            "response.failed", "response.incomplete", "response.error", "error")
        while True:
            line, cut = lines.line()
            if not line and response.done:
                break
            if not line:
                event_name = ""
                continue
            if line.startswith(b"event:"):
                event_name = _text(line[6:]).strip()
                continue
            if not line.startswith(b"data:") or (event_name and event_name not in accepted):
                continue
            if cut:
                continue
            payload = line[5:].strip()
            if payload == b"[DONE]":
                break
            try:
                event = json.loads(_text(payload))
            except Exception:
                continue
            kind = event_name or event.get("type", "")
            if kind == "response.output_text.delta":
                delta = event.get("delta", "")
                if delta:
                    parts.append(delta)
                    if on_delta:
                        on_delta(delta)
            elif kind == "response.output_text.done" and not parts:
                text = event.get("text", "")
                if text:
                    parts.append(text)
                    if on_delta:
                        on_delta(text)
            elif kind in accepted[2:]:
                try:
                    error = (event.get("error", {}).get("message") or
                             event.get("response", {}).get("error", {}).get("message") or
                             event.get("message"))
                except Exception:
                    pass
        answer = "".join(parts)
        return status, answer or None, None if answer else (error or "GPT BOS YANIT VERDI")
    finally:
        body = None
        parts = None
        if secure is not None:
            try:
                secure.close()
            except Exception:
                pass
        elif sock is not None:
            try:
                sock.close()
            except Exception:
                pass
        gc.collect()
