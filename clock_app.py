# -*- coding: utf-8 -*-
# Raspberry Pi Pico 2 W + ST7789 320x240 dokunmatik ekran ile MASA SAATI
# Ayni kart ve ekran (Waveshare Pico-ResTouch-LCD tarzi). Thonny'de main.py olarak kaydet.
#
# OZELLIKLER:
#  - Buyuk 7-segment HH:MM, yanip sonen iki nokta, altinda saniye cubugu
#  - Gun + tarih (Turkce, ASCII)
#  - WiFi varsa NTP ile otomatik saat ayari (internetten dogru saat)
#  - Dokunmatik: AYARLAR/GPT tuslari altta
#    her zaman gorunur.
#    Saat bicimi sabit 24 saattir.
#
# ==== KULLANICI AYARLARI ====
WIFI_SSID = ""          # WiFi adi (bos birakirsan internet kullanmaz, elle ayar yaparsin)
WIFI_PASS = ""
TZ_OFFSET = 3
USE_24H = True
NTP_EVERY_MS = 3600000
WIFI_RETRY_MS = 10000
WIFI_BOOT_RETRY_MS = 6000
WIFI_BOOT_RETRY_COUNT = 3
WIFI_BOOT_CONNECT_TIMEOUT_MS = 6000
GC_EVERY_MS = 300000


MANUAL_LOCATION = ""


# ==== SOR (ChatGPT) AYARLARI ====
OPENAI_API_KEY = ""
APP_VERSION = "1.0.32"
OTA_MANIFEST_URL = "https://raw.githubusercontent.com/ysnkrt/masa-saati-ota/main/ota.json"
OTA_MAX_BYTES = 350000
OTA_RELEASE_FILE = "ota_release.txt"
LIVE_CACHE_SECONDS = 180
LIVE_CACHE_LIMIT = 6
LIVE_CACHE_PREFIX = "guncel_"

USER_COUNTRY = "TR"
USER_CITY = "Istanbul"
USER_REGION = "Istanbul"
USER_LAT = None
USER_LON = None
# ============================


SIZE_PROFILES = [(10, 14, 11, 20), (8, 11, 9, 16), (6, 8, 7, 12)]
SIZE_NAMES = ["BUYUK", "ORTA", "KUCUK"]

LEN_PROFILES = [
    ("UZUN", 900, "Cevabini detayli ve kapsamli ver."),
    ("NORMAL", 350, "Cevabini orta uzunlukta ozetle."),
    ("KISA", 200, "Cevabini cok kisa, 1-2 cumlede ver."),
]
ans_size_idx = 1
ans_len_idx = 1
anim_on = True
UI_FRAME_MS = 80
MAIN_LOOP_MS = 12
TOUCH_IDLE_POLL_MS = 22
LONG_PRESS_MS = 650
TOUCH_DEBOUNCE_MS = 140


weather_idx = 2

# ==== NAMAZ VAKITLERI ====

PRAYER_CITY = "Istanbul"
PRAYER_COUNTRY = "Turkey"
PRAYER_METHOD = 13
PRAYER_EVERY_MS = 21600000
PRAYER_MODE_NAMES = ["KAPALI", "YAKIN", "HEPSI"]
prayer_mode_idx = 1
PRAYER_SIZE_NAMES = ["KUCUK", "ORTA", "BUYUK"]
PRAYER_SIZE_STYLES = ((5, 7, 6), (7, 10, 8), (9, 13, 10))
prayer_size_idx = 1
PRAYER_THICK_NAMES = ["INCE"]
prayer_thick_idx = 0
PRAYER_GAP_NAMES = ["SIK", "NORMAL", "GENIS"]
prayer_gap_idx = 1

import machine
from machine import Pin, SPI, PWM, ADC
try:
    from machine import WDT, Timer
except Exception:
    WDT = None
    Timer = None
try:
    from machine import freq as machine_freq
except Exception:
    machine_freq = None
import time
import gc
import math
import sys

try:
    import os
except Exception:
    import uos as os
if not OPENAI_API_KEY.strip():
    try:
        _key_file = open("openai_key.txt")
        OPENAI_API_KEY = _key_file.read().strip()
        _key_file.close()
        _key_file = None
    except Exception:
        pass
try:
    import json
except Exception:
    import ujson as json
try:
    import hashlib
except Exception:
    try:
        import uhashlib as hashlib
    except Exception:
        hashlib = None
try:
    import socket
except Exception:
    socket = None
try:
    import ssl
except Exception:
    ssl = None
try:
    import select
except Exception:
    try:
        import uselect as select
    except Exception:
        select = None

try:
    import network
except Exception:
    network = None
try:
    import ntptime
except Exception:
    ntptime = None

rtc = None
try:
    from machine import RTC
    rtc = RTC()
except Exception:
    rtc = None
try:
    from machine import reset as machine_reset
except Exception:
    machine_reset = None


def safe_write_text(path, data):
    """Dosyayi once gecici dosyaya yazar; yarim ayar dosyasi birakmaz."""
    tmp = path + ".tmp"
    f = None
    try:
        f = open(tmp, "w")
        f.write(data)
        try:
            f.flush()
        except Exception:
            pass
        f.close()
        f = None
        replace = getattr(os, "replace", None)
        if replace is not None:
            replace(tmp, path)
        else:
            try:
                os.remove(path)
            except Exception:
                pass
            os.rename(tmp, path)
        return True
    except Exception:
        if f is not None:
            try:
                f.close()
            except Exception:
                pass
        try:
            os.remove(tmp)
        except Exception:
            pass
        return False

# ---- Pinler (satranc projesiyle ayni, dogrulandi) ----
LCD_DC = 8; LCD_CS = 9; LCD_SCK = 10; LCD_MOSI = 11; LCD_MISO = 12
LCD_BL = 13; LCD_RST = 15
TP_CS = 16

LCD_BAUD = 24000000
TOUCH_BAUD = 2000000

WIDTH = 320
HEIGHT = 240

# ---- Renkler (RGB565) ----
BLACK = 0x0000
WHITE = 0xFFFF
GRAY = 0x8410
DGRAY = 0x2104
DARKGRAY = 0x4208
YELLOW = 0xFFE0
GREEN = 0x07E0
RED = 0xF800
CYAN = 0x07FF
AMBER = 0xFD20
MAGENTA = 0xF81F
BLUE = 0x041F
DARKBLUE = 0x0010
ORANGE = 0xFC00
PURPLE = 0x8010
PINK = 0xF81F
LIME = 0x87E0
LGRAY = 0xC618


mode_idx = 0

BG = BLACK
FG = WHITE
FG_DIM = DGRAY
RAIN_COL = CYAN
RING_FULL = WHITE
RING_EMPTY = DARKGRAY
TAB_UNSEL = DARKGRAY
TITLE_COL = CYAN
LOCK_CLOSED_COL = GRAY


def apply_mode():
    global BG, FG, FG_DIM, RAIN_COL, RING_FULL, RING_EMPTY, TAB_UNSEL
    global TITLE_COL, LOCK_CLOSED_COL
    BG = BLACK
    FG = WHITE
    FG_DIM = DGRAY
    RAIN_COL = CYAN
    RING_FULL = WHITE
    RING_EMPTY = DARKGRAY
    TAB_UNSEL = DARKGRAY
    TITLE_COL = CYAN
    LOCK_CLOSED_COL = GRAY
    _rebuild_ans_zero_buffers()


BRIGHT_LEVELS = [65535, 49151, 32768, 16384, 655]
BRIGHT_NAMES = ["%100", "%75", "%50", "%25", "%1"]
bright_idx = 0
BRIGHT_MIN = 655
bright_value = BRIGHT_LEVELS[bright_idx]


screen_flip = False


face_idx = 0
FACE_COUNT = 4

# ---- Dokunmatik eslemesi ----
RAW_X_MIN = 300
RAW_X_MAX = 3900
RAW_Y_MIN = 300
RAW_Y_MAX = 3900
TOUCH_CAL_FILE = "touch_cal.txt"


def clamp(v, mn, mx):
    if v < mn:
        return mn
    if v > mx:
        return mx
    return v


def map_value(v, in_min, in_max, out_min, out_max):
    if in_max == in_min:
        return out_min
    return int((v - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def load_touch_cal():
    global RAW_X_MIN, RAW_X_MAX, RAW_Y_MIN, RAW_Y_MAX
    f = None
    try:
        f = open(TOUCH_CAL_FILE, "r")
        values = [int(v) for v in f.read().split()]
        f.close()
        f = None
        if len(values) != 4:
            return False
        x_min, x_max, y_min, y_max = values
        if (100 <= x_min < x_max <= 4050 and
                100 <= y_min < y_max <= 4050 and
                x_max - x_min >= 1200 and y_max - y_min >= 1200):
            RAW_X_MIN, RAW_X_MAX = x_min, x_max
            RAW_Y_MIN, RAW_Y_MAX = y_min, y_max
            return True
    except Exception:
        if f is not None:
            try:
                f.close()
            except Exception:
                pass
    return False


GUNLER = ["PAZARTESI", "SALI", "CARSAMBA", "PERSEMBE", "CUMA", "CUMARTESI", "PAZAR"]
AYLAR = ["OCAK", "SUBAT", "MART", "NISAN", "MAYIS", "HAZIRAN",
         "TEMMUZ", "AGUSTOS", "EYLUL", "EKIM", "KASIM", "ARALIK"]


FONT = {
    "A":["01110","10001","10001","11111","10001","10001","10001"],
    "B":["11110","10001","10001","11110","10001","10001","11110"],
    "C":["01111","10000","10000","10000","10000","10000","01111"],
    "D":["11110","10001","10001","10001","10001","10001","11110"],
    "E":["11111","10000","10000","11110","10000","10000","11111"],
    "G":["01111","10000","10000","10111","10001","10001","01111"],
    "H":["10001","10001","10001","11111","10001","10001","10001"],
    "I":["11111","00100","00100","00100","00100","00100","11111"],
    "K":["10001","10010","10100","11000","10100","10010","10001"],
    "L":["10000","10000","10000","10000","10000","10000","11111"],
    "M":["10001","11011","10101","10101","10001","10001","10001"],
    "N":["10001","11001","10101","10011","10001","10001","10001"],
    "O":["01110","10001","10001","10001","10001","10001","01110"],
    "P":["11110","10001","10001","11110","10000","10000","10000"],
    "R":["11110","10001","10001","11110","10100","10010","10001"],
    "S":["01111","10000","10000","01110","00001","00001","11110"],
    "T":["11111","00100","00100","00100","00100","00100","00100"],
    "U":["10001","10001","10001","10001","10001","10001","01110"],
    "Y":["10001","10001","01010","00100","00100","00100","00100"],
    "F":["11111","10000","10000","11110","10000","10000","10000"],
    "J":["00111","00010","00010","00010","10010","10010","01100"],
    "Q":["01110","10001","10001","10001","10101","10010","01101"],
    "V":["10001","10001","10001","10001","01010","01010","00100"],
    "W":["10001","10001","10001","10101","10101","11011","10001"],
    "X":["10001","10001","01010","00100","01010","10001","10001"],
    "Z":["11111","00001","00010","00100","01000","10000","11111"],
    "!":["00100","00100","00100","00100","00100","00000","00100"],
    ".":["00000","00000","00000","00000","00000","00110","00110"],
    ",":["00000","00000","00000","00000","00110","00110","01100"],
    "?":["01110","10001","00001","00010","00100","00000","00100"],
    "-":["00000","00000","00000","11111","00000","00000","00000"],
    "/":["00001","00010","00100","00100","01000","10000","10000"],
    "'":["00100","00100","01000","00000","00000","00000","00000"],
    "(":["00010","00100","01000","01000","01000","00100","00010"],
    ")":["01000","00100","00010","00010","00010","00100","01000"],
    "0":["01110","10001","10011","10101","11001","10001","01110"],
    "1":["00100","01100","00100","00100","00100","00100","01110"],
    "2":["01110","10001","00001","00010","00100","01000","11111"],
    "3":["11110","00001","00001","01110","00001","00001","11110"],
    "4":["00010","00110","01010","10010","11111","00010","00010"],
    "5":["11111","10000","10000","11110","00001","00001","11110"],
    "6":["01110","10000","10000","11110","10001","10001","01110"],
    "7":["11111","00001","00010","00100","01000","01000","01000"],
    "8":["01110","10001","10001","01110","10001","10001","01110"],
    "9":["01110","10001","10001","01111","00001","00001","01110"],
    ":":["00000","00100","00100","00000","00100","00100","00000"],
    " ":["00000","00000","00000","00000","00000","00000","00000"],
}

FONT.update({
    "a":["00000","00000","01110","00001","01111","10001","01111"],
    "b":["10000","10000","11110","10001","10001","10001","11110"],
    "c":["00000","00000","01111","10000","10000","10000","01111"],
    "d":["00001","00001","01111","10001","10001","10001","01111"],
    "e":["00000","00000","01110","10001","11111","10000","01110"],
    "f":["00110","01001","01000","11100","01000","01000","01000"],
    "g":["00000","01111","10001","10001","01111","00001","01110"],
    "h":["10000","10000","11110","10001","10001","10001","10001"],
    "i":["00100","00000","01100","00100","00100","00100","01110"],
    "j":["00010","00000","00110","00010","00010","10010","01100"],
    "k":["10000","10000","10010","10100","11000","10100","10010"],
    "l":["01100","00100","00100","00100","00100","00100","01110"],
    "m":["00000","00000","11010","10101","10101","10101","10101"],
    "n":["00000","00000","10110","11001","10001","10001","10001"],
    "o":["00000","00000","01110","10001","10001","10001","01110"],
    "p":["00000","11110","10001","10001","11110","10000","10000"],
    "q":["00000","01111","10001","10001","01111","00001","00001"],
    "r":["00000","00000","10110","11001","10000","10000","10000"],
    "s":["00000","00000","01111","10000","01110","00001","11110"],
    "t":["01000","01000","11100","01000","01000","01001","00110"],
    "u":["00000","00000","10001","10001","10001","10011","01101"],
    "v":["00000","00000","10001","10001","10001","01010","00100"],
    "w":["00000","00000","10001","10001","10101","10101","01010"],
    "x":["00000","00000","10001","01010","00100","01010","10001"],
    "y":["00000","10001","10001","10001","01111","00001","01110"],
    "z":["00000","00000","11111","00010","00100","01000","11111"],
    "@":["01110","10001","10111","10101","10111","10000","01110"],
    "#":["01010","01010","11111","01010","11111","01010","01010"],
    "$":["00100","01111","10100","01110","00101","11110","00100"],
    "&":["01100","10010","10100","01000","10101","10010","01101"],
    "*":["00000","10101","01110","11111","01110","10101","00000"],
    "_":["00000","00000","00000","00000","00000","00000","11111"],
    "+":["00000","00100","00100","11111","00100","00100","00000"],
    "=":["00000","00000","11111","00000","11111","00000","00000"],
    "%":["11001","11010","00010","00100","01000","01011","10011"],
})


class ST7789:
    def __init__(self, spi, cs, dc, rst, bl, width=320, height=240):
        self.spi = spi
        self.width = width
        self.height = height
        self.cs = Pin(cs, Pin.OUT)
        self.dc = Pin(dc, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)
        self.bl = Pin(bl, Pin.OUT)
        self.cs.value(1)
        self.dc.value(1)
        self.bl.value(1)
        self._one = bytearray(1)
        self._window = bytearray(4)
        self._line_cache = {}
        self._line_cache_order = []
        self.reset()
        self.init_display()

    def reset(self):
        self.rst.value(1); time.sleep_ms(50)
        self.rst.value(0); time.sleep_ms(50)
        self.rst.value(1); time.sleep_ms(150)

    def write_cmd(self, cmd):
        one = self._one
        one[0] = cmd
        self.dc.value(0); self.cs.value(0)
        self.spi.write(one)
        self.cs.value(1)

    def write_data(self, data):
        self.dc.value(1); self.cs.value(0)
        if isinstance(data, int):
            self._one[0] = data
            self.spi.write(self._one)
        else:
            self.spi.write(data)
        self.cs.value(1)

    def init_display(self):
        self.write_cmd(0x01); time.sleep_ms(150)
        self.write_cmd(0x11); time.sleep_ms(120)
        self.write_cmd(0x3A); self.write_data(0x55)
        self.write_cmd(0x36); self.write_data(0x70)
        self.write_cmd(0x21); time.sleep_ms(10)
        self.write_cmd(0x13); time.sleep_ms(10)
        self.write_cmd(0x29); time.sleep_ms(100)

    def set_rotation(self, flip):

        self.write_cmd(0x36)
        self.write_data(0xB0 if flip else 0x70)

    def set_window(self, x0, y0, x1, y1):
        win = self._window
        self.write_cmd(0x2A)
        win[0] = x0 >> 8
        win[1] = x0 & 0xFF
        win[2] = x1 >> 8
        win[3] = x1 & 0xFF
        self.write_data(win)
        self.write_cmd(0x2B)
        win[0] = y0 >> 8
        win[1] = y0 & 0xFF
        win[2] = y1 >> 8
        win[3] = y1 & 0xFF
        self.write_data(win)
        self.write_cmd(0x2C)

    def _solid_line(self, w, color):
        key = (w, color)
        line = self._line_cache.get(key)
        if line is not None:
            return line
        line = bytes([color >> 8, color & 0xFF]) * w
        if len(self._line_cache_order) >= 12:
            old = self._line_cache_order.pop(0)
            self._line_cache.pop(old, None)
        self._line_cache[key] = line
        self._line_cache_order.append(key)
        return line

    def fill_rect(self, x, y, w, h, color):
        x = int(x); y = int(y); w = int(w); h = int(h)
        if x < 0:
            w += x; x = 0
        if y < 0:
            h += y; y = 0
        if x + w > self.width:
            w = self.width - x
        if y + h > self.height:
            h = self.height - y
        if w <= 0 or h <= 0:
            return
        self.set_window(x, y, x + w - 1, y + h - 1)
        line = self._solid_line(w, color)
        self.dc.value(1); self.cs.value(0)
        for _ in range(h):
            self.spi.write(line)
        self.cs.value(1)

    def fill(self, color):
        self.fill_rect(0, 0, self.width, self.height, color)

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def rect(self, x, y, w, h, color):
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)

    def circle(self, cx, cy, r, color):

        rr = r * r
        for yy in range(-r, r + 1):
            xx = r
            y2 = yy * yy
            while xx > 0 and xx * xx + y2 > rr:
                xx -= 1
            self.fill_rect(cx - xx, cy + yy, xx * 2 + 1, 1, color)

    def ring(self, cx, cy, r, color):

        x = r; y = 0; err = 0
        while x >= y:
            for (px, py) in ((x, y), (y, x), (-y, x), (-x, y),
                             (-x, -y), (-y, -x), (y, -x), (x, -y)):
                self.fill_rect(cx + px, cy + py, 1, 1, color)
            y += 1
            if err <= 0:
                err += 2 * y + 1
            if err > 0:
                x -= 1
                err -= 2 * x + 1

    def line(self, x0, y0, x1, y1, color):
        x0 = int(x0); y0 = int(y0); x1 = int(x1); y1 = int(y1)
        dx = abs(x1 - x0); dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0, y0, 1, 1, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def text(self, text, x, y, color, size=1):
        start_x = x
        for ch in text:
            if ch == "\n":
                y += 8 * size; x = start_x; continue
            if ch in FONT:
                data = FONT[ch]
            else:
                uch = ch.upper()
                data = FONT[uch] if uch in FONT else FONT[" "]
            for row in range(7):
                bits = data[row]
                col = 0
                while col < 5:
                    while col < 5 and bits[col] != "1":
                        col += 1
                    start = col
                    while col < 5 and bits[col] == "1":
                        col += 1
                    if start < col:
                        self.fill_rect(x + start * size, y + row * size,
                                       (col - start) * size, size, color)
            x += 6 * size


class XPT2046:
    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT)
        self.cs.value(1)
        self._tx = bytearray(3)
        self._rx = bytearray(3)

    def read_axis(self, cmd):
        tx = self._tx
        rx = self._rx
        tx[0] = cmd
        tx[1] = 0
        tx[2] = 0
        self.cs.value(0)
        self.spi.write_readinto(tx, rx)
        self.cs.value(1)
        return ((rx[1] << 8) | rx[2]) >> 3

    def _map_xy(self, raw_x, raw_y):
        x = map_value(raw_y, RAW_Y_MIN, RAW_Y_MAX, 0, WIDTH - 1)
        y = map_value(raw_x, RAW_X_MIN, RAW_X_MAX, 0, HEIGHT - 1)
        x = WIDTH - 1 - x
        if screen_flip:
            x = WIDTH - 1 - x
            y = HEIGHT - 1 - y
        return clamp(x, 0, WIDTH - 1), clamp(y, 0, HEIGHT - 1)

    def read_raw(self):
        _watchdog_touch()
        self.spi.init(baudrate=TOUCH_BAUD, polarity=0, phase=0)
        try:
            xs = []; ys = []
            for _ in range(12):
                x = self.read_axis(0xD0)
                y = self.read_axis(0x90)
                z1 = self.read_axis(0xB0)
                if 150 <= x <= 4050 and 150 <= y <= 4050 and z1 > 50:
                    xs.append(x); ys.append(y)
                time.sleep_ms(2)
            if len(xs) < 5:
                return None
            xs.sort(); ys.sort()
            mid = len(xs) // 2
            return xs[mid], ys[mid]
        finally:
            self.spi.init(baudrate=LCD_BAUD, polarity=0, phase=0)

    def read_screen(self):
        raw = self.read_raw()
        if raw is None:
            return None
        x, y = self._map_xy(raw[0], raw[1])
        return raw[0], raw[1], x, y

    def read_fast(self):
        _watchdog_touch()
        self.spi.init(baudrate=TOUCH_BAUD, polarity=0, phase=0)
        try:
            xs = []; ys = []
            for _ in range(5):
                x = self.read_axis(0xD0)
                y = self.read_axis(0x90)
                z1 = self.read_axis(0xB0)
                if z1 > 50 and 150 <= x <= 4050 and 150 <= y <= 4050:
                    xs.append(x); ys.append(y)
            if len(xs) < 3:
                return None
            xs.sort(); ys.sort()
            return self._map_xy(xs[len(xs) // 2], ys[len(ys) // 2])
        finally:
            self.spi.init(baudrate=LCD_BAUD, polarity=0, phase=0)


# ===================== SOR (ChatGPT) =====================
TR_MAP = {
    "\u00e7": "c", "\u00c7": "C", "\u015f": "s", "\u015e": "S",
    "\u011f": "g", "\u011e": "G", "\u00fc": "u", "\u00dc": "U",
    "\u00f6": "o", "\u00d6": "O", "\u0131": "i", "\u0130": "I",
    "\u00e2": "a", "\u00c2": "A", "\u00ee": "i", "\u00ce": "I",
    "\u00fb": "u", "\u00db": "U",
}


def to_screen_text(s):
    out = ""
    for ch in s:
        if ch in TR_MAP:
            ch = TR_MAP[ch]
        if ch == "\n":
            out += "\n"
        elif ch == "\r" or ch == "\t":
            out += " "
        elif ch in FONT:
            out += ch
        else:
            out += " "
    return out


def strip_urls(s):
    out = []
    i = 0
    n = len(s)
    low = s.lower()
    while i < n:
        if low.startswith("http", i) or low.startswith("www.", i):
            while i < n and not s[i].isspace():
                i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def wrap_full(text, width):
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            while len(w) > width:
                if cur:
                    lines.append(cur); cur = ""
                lines.append(w[:width])
                w = w[width:]
            if cur == "":
                cur = w
            elif len(cur) + 1 + len(w) <= width:
                cur = cur + " " + w
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines


ANS_TOP = 24
ANS_BOTTOM = 206


_AGW = 8
_AGH = 11
_AADV = 9
ANS_LINE_H = 16
ANS_CHARS = (WIDTH - 8) // _AADV
ANS_VISIBLE = (ANS_BOTTOM - ANS_TOP) // ANS_LINE_H
_ANS_BUF = None
_ANS_BUF_IDX = -1


def _fill_answer_background(zero):
    if zero is None:
        return
    hi = BG >> 8
    lo = BG & 0xFF
    chunk = bytes([hi, lo]) * 32
    chunk_len = len(chunk)
    full = len(zero) - len(zero) % chunk_len
    for start in range(0, full, chunk_len):
        zero[start:start + chunk_len] = chunk
    if full < len(zero):
        zero[full:] = chunk[:len(zero) - full]


def _rebuild_ans_zero_buffers():
    _fill_answer_background(_ANS_BUF)


def release_answer_buffers():
    global _ANS_BUF, _ANS_BUF_IDX
    _ANS_BUF = None
    _ANS_BUF_IDX = -1
    gc.collect()


def apply_ans_size(idx):
    global _AGW, _AGH, _AADV, ANS_LINE_H, ANS_CHARS, ANS_VISIBLE
    global _ANS_BUF, _ANS_BUF_IDX
    idx = idx % len(SIZE_PROFILES)
    AGW, AGH, AADV, LH = SIZE_PROFILES[idx]
    if _ANS_BUF is None or _ANS_BUF_IDX != idx:
        _ANS_BUF = None
        _ANS_BUF_IDX = -1
        gc.collect()
        size = WIDTH * LH * 2
        _ANS_BUF = bytearray(size)
        _ANS_BUF_IDX = idx
    _fill_answer_background(_ANS_BUF)
    _AGW = AGW
    _AGH = AGH
    _AADV = AADV
    ANS_LINE_H = LH
    ANS_CHARS = (WIDTH - 8) // AADV
    ANS_VISIBLE = (ANS_BOTTOM - ANS_TOP) // LH


def render_answer_line(text, screen_y):
    buf = _ANS_BUF
    _fill_answer_background(buf)
    w = WIDTH
    cx = 4
    limit = w - _AADV
    th = FG
    hi = th >> 8
    lo = th & 0xFF
    for ch in text:
        glyph = FONT[ch] if ch in FONT else FONT.get(ch.upper(), FONT[" "])
        for dy in range(_AGH):
            row = glyph[dy * 7 // _AGH]
            base = dy * w + cx
            for dx in range(_AGW):
                if row[dx * 5 // _AGW] == "1":
                    pos = (base + dx) * 2
                    buf[pos] = hi
                    buf[pos + 1] = lo
        cx += _AADV
        if cx > limit:
            break
    draw_y0 = max(ANS_TOP, screen_y)
    draw_y1 = min(ANS_BOTTOM, screen_y + ANS_LINE_H)
    if draw_y0 >= draw_y1:
        return
    source_row = draw_y0 - screen_y
    source_start = source_row * w * 2
    source_end = source_start + (draw_y1 - draw_y0) * w * 2
    lcd.set_window(0, draw_y0, w - 1, draw_y1 - 1)
    lcd.dc.value(1)
    lcd.cs.value(0)
    lcd.spi.write(memoryview(buf)[source_start:source_end])
    lcd.cs.value(1)


def draw_answer_frame(scrollable=True):
    lcd.fill(BG)
    lcd.text("GPT:", 4, 4, GREEN, 2)
    buttons = (
        (0, 68, BLUE, "GERI", WHITE),
        (70, 70, GREEN, "YENI", BLACK),
        (142, 88, DARKGRAY, "YUKARI", WHITE),
        (232, 88, DARKGRAY, "ASAGI", WHITE),
    )
    for x, w, color, label, fg in buttons:
        lcd.fill_rect(x, 210, w, 30, color)
        lcd.rect(x, 210, w, 30, GRAY)
        lcd.text(label, x + (w - len(label) * 8) // 2, 219, fg, 1)


def draw_answer_text_pixels(lines, scroll_px):
    n = len(lines)
    first = scroll_px // ANS_LINE_H
    shift = scroll_px % ANS_LINE_H
    rows = ANS_VISIBLE + (2 if shift else 0)
    i = first
    for row in range(rows):
        screen_y = ANS_TOP - shift + row * ANS_LINE_H
        render_answer_line(lines[i] if i < n else "", screen_y)
        i += 1
    if n > ANS_VISIBLE:
        track_h = ANS_BOTTOM - ANS_TOP
        bar_h = max(12, track_h * ANS_VISIBLE // n)
        max_scroll = (n - ANS_VISIBLE) * ANS_LINE_H
        bar_y = ANS_TOP + (track_h - bar_h) * scroll_px // max_scroll
        lcd.fill_rect(WIDTH - 4, ANS_TOP, 3, track_h, DARKGRAY)
        lcd.fill_rect(WIDTH - 4, bar_y, 3, bar_h, CYAN)


def draw_answer_text(lines, offset):
    draw_answer_text_pixels(lines, offset * ANS_LINE_H)


def show_answer(lines):
    max_off = len(lines) - ANS_VISIBLE
    if max_off < 0:
        max_off = 0
    max_scroll = max_off * ANS_LINE_H
    drag_px = 0
    offset = 0
    target_offset = 0
    draw_answer_frame()
    draw_answer_text(lines, offset)
    page_step = ANS_VISIBLE - 2
    if page_step < 1:
        page_step = 1
    last_y = None
    last_draw = time.ticks_ms()
    while True:
        res = touch.read_fast()
        if res is None:
            if last_y is not None and target_offset != offset:
                offset = target_offset
                draw_answer_text(lines, offset)
                last_draw = time.ticks_ms()
            last_y = None
            time.sleep_ms(2)
            continue
        x, y = res
        if last_y is None:
            if y >= 210:
                if x < 70:
                    time.sleep_ms(120)
                    return "back"
                if x < 142:
                    time.sleep_ms(120)
                    return "new"
                if x < 232:
                    target_offset -= page_step
                else:
                    target_offset += page_step
                if target_offset < 0:
                    target_offset = 0
                elif target_offset > max_off:
                    target_offset = max_off
                drag_px = target_offset * ANS_LINE_H
                if target_offset != offset:
                    offset = target_offset
                    draw_answer_text(lines, offset)
                    last_draw = time.ticks_ms()
                while touch.read_fast() is not None:
                    time.sleep_ms(10)
                last_y = None
                continue
            last_y = y
            continue
        dy = y - last_y
        last_y = y
        drag_px -= dy
        if drag_px < 0:
            drag_px = 0
        elif drag_px > max_scroll:
            drag_px = max_scroll
        target_offset = (drag_px + ANS_LINE_H // 2) // ANS_LINE_H
        now = time.ticks_ms()
        if (target_offset != offset and
                time.ticks_diff(now, last_draw) >= 35):
            offset = target_offset
            draw_answer_text(lines, offset)
            last_draw = time.ticks_ms()


def _buffer_find(data, needle, start=0):
    needle_len = len(needle)
    if needle_len == 0:
        return start
    limit = len(data) - needle_len
    first = needle[0]
    while start <= limit:
        if data[start] == first:
            matched = True
            for offset in range(1, needle_len):
                if data[start + offset] != needle[offset]:
                    matched = False
                    break
            if matched:
                return start
        start += 1
    return -1


def _decode_buffer(data):
    if isinstance(data, bytearray):
        data = bytes(data)
    try:
        return data.decode("utf-8")
    except Exception:
        return data.decode()


def _dechunk(data):
    out = bytearray()
    i = 0
    L = len(data)
    while i < L:
        j = _buffer_find(data, b"\r\n", i)
        if j < 0:
            break
        try:
            size_text = _decode_buffer(data[i:j]).split(";", 1)[0].strip()
            n = int(size_text, 16)
        except ValueError:
            break
        if n == 0:
            break
        start = j + 2
        out.extend(data[start:start + n])
        i = start + n + 2
    return out










def https_get(host, path, timeout=25, extra_headers=""):
    if socket is None or ssl is None:
        return 0, ""
    s = None
    ss = None
    raw = None
    try:
        _watchdog_touch()
        gc.collect()
        addr = socket.getaddrinfo(host, 443)[0][-1]
        s = socket.socket()
        try:
            s.settimeout(timeout)
        except Exception:
            pass
        s.connect(addr)
        try:
            ss = ssl.wrap_socket(s, server_hostname=host)
        except TypeError:
            ss = ssl.wrap_socket(s)
        req = ("GET " + path + " HTTP/1.1\r\n"
               "Host: " + host + "\r\n"
               "User-Agent: masasaati-pico/1.0\r\n"
               "Accept: application/json\r\n"
               + extra_headers +
               "Connection: close\r\n\r\n")
        ss.write(req.encode("utf-8"))
        raw = bytearray()
        read_started = time.ticks_ms()
        while True:
            d = ss.read(512)
            _watchdog_touch()
            if d is None:
                if time.ticks_diff(time.ticks_ms(), read_started) >= timeout * 1000:
                    break
                _gpt_wait_step()
                time.sleep_ms(10)
                continue
            if len(d) == 0:
                break
            raw.extend(d)
            _gpt_wait_step()
        he = _buffer_find(raw, b"\r\n\r\n")
        if he < 0:
            return 0, ""
        head = bytes(raw[:he])
        raw = raw[he + 4:]
        try:
            status = int(head.split(b"\r\n")[0].split(b" ")[1])
        except Exception:
            status = 0
        if head.lower().find(b"transfer-encoding: chunked") >= 0:
            body_bytes = _dechunk(raw)
            raw = None
        else:
            body_bytes = raw
            raw = None
        text = _decode_buffer(body_bytes)
        body_bytes = None
        return status, text
    finally:
        raw = None
        if ss is not None:
            try:
                ss.close()
            except Exception:
                pass
        elif s is not None:
            try:
                s.close()
            except Exception:
                pass
        gc.collect()


 


















 

















































def is_online():
    if network is None:
        return False
    try:
        w = network.WLAN(network.STA_IF)
        return w.isconnected()
    except Exception:
        return False


geo_ok = False


def _geo_try_ipapi():
    status, text = https_get("ipapi.co", "/json/", 12)
    if status != 200 or not text:
        return None
    data = json.loads(text)
    region = data.get("region")
    cc = data.get("country_code")
    cname = data.get("country_name")
    lat = data.get("latitude")
    lon = data.get("longitude")
    if not region or not cc:
        return None
    return region, cc, cname, lat, lon


def _geo_try_ipwho():


    status, text = https_get("ipwho.is", "/", 12)
    if status != 200 or not text:
        return None
    data = json.loads(text)
    if data.get("success") is False:
        return None
    region = data.get("region")
    cc = data.get("country_code")
    cname = data.get("country")
    lat = data.get("latitude")
    lon = data.get("longitude")
    if not region or not cc:
        return None
    return region, cc, cname, lat, lon


def geo_locate():


    global USER_COUNTRY, USER_CITY, USER_REGION, USER_LAT, USER_LON
    global PRAYER_CITY, PRAYER_COUNTRY, geo_ok
    if not is_online():
        return False
    result = None
    for fn in (_geo_try_ipapi, _geo_try_ipwho):
        try:
            result = fn()
        except Exception:
            result = None
        if result is not None:
            break
    gc.collect()
    if result is None:
        return False
    region, cc, cname, lat, lon = result
    if MANUAL_LOCATION:
        region = MANUAL_LOCATION
    USER_CITY = region
    USER_REGION = region
    USER_COUNTRY = cc
    PRAYER_CITY = region
    PRAYER_COUNTRY = cname if cname else cc
    if lat is not None and lon is not None:
        USER_LAT = lat
        USER_LON = lon
    geo_ok = True
    return True


# ==== OTOMATIK ISIK: gun batimindan 30 dk sonra kis, gun dogumundan ====
# ==== 30 dk once (yeniden) tam parlakliga getir ====
DIM_AFTER_SUNSET_MIN = 30
BRIGHTEN_BEFORE_SUNRISE_MIN = 30
DIM_AT_MIN = -1
BRIGHTEN_AT_MIN = -1
_sunset_day_key = ""
_dimmed_today = False
_brightened_today = False


def _parse_hm(s):

    parts = s.strip().split(":")
    return int(parts[0]), int(parts[1])


def sunset_sync():


    global DIM_AT_MIN, BRIGHTEN_AT_MIN, _sunset_day_key
    global _dimmed_today, _brightened_today
    if not is_online() or USER_LAT is None or USER_LON is None:
        return False
    try:
        path = "/json?lat=%s&lng=%s&time_format=24" % (str(USER_LAT), str(USER_LON))
        status, text = https_get("api.sunrisesunset.io", path, 12)
        if status != 200 or not text:
            return False
        data = json.loads(text)
        h, m = _parse_hm(data["results"]["sunset"])
        total = h * 60 + m + DIM_AFTER_SUNSET_MIN
        if total >= 1440:
            total -= 1440
        DIM_AT_MIN = total
        h, m = _parse_hm(data["results"]["sunrise"])
        total = h * 60 + m - BRIGHTEN_BEFORE_SUNRISE_MIN
        if total < 0:
            total = 0
        BRIGHTEN_AT_MIN = total
        lt = time.localtime()
        _sunset_day_key = "%04d-%02d-%02d" % (lt[0], lt[1], lt[2])
        _dimmed_today = False
        _brightened_today = False
        return True
    except Exception:
        return False
    finally:
        gc.collect()


def _urlenc(s):

    out = ""
    for ch in s:
        if ch == " ":
            out += "%20"
        else:
            out += ch
    return out


def _prayer_key(lt):
    return "%04d-%02d-%02d" % (lt[0], lt[1], lt[2])


def prayer_sync():

    global prayer_text, prayer_times, prayer_day_key, last_prayer_sync
    if not is_online():
        return False
    lt = time.localtime()
    key = _prayer_key(lt)
    if prayer_day_key == key and prayer_times:
        return True
    try:
        path = ("/v1/timingsByCity/%02d-%02d-%04d?city=%s&country=%s&method=%d" %
                (lt[2], lt[1], lt[0], _urlenc(PRAYER_CITY),
                 _urlenc(PRAYER_COUNTRY), PRAYER_METHOD))
        status, text = https_get("api.aladhan.com", path, 25)
        if status != 200 or not text:
            return False
        data = json.loads(text)
        t = data["data"]["timings"]
        im = t.get("Fajr", "")[:5]
        og = t.get("Dhuhr", "")[:5]
        ik = t.get("Asr", "")[:5]
        ak = t.get("Maghrib", "")[:5]
        ya = t.get("Isha", "")[:5]
        if not (im and og and ik and ak and ya):
            return False
        prayer_times = [("IM", im), ("OG", og), ("IK", ik), ("AK", ak), ("YA", ya)]
        prayer_text = "IM %s OG %s IK %s AK %s YA %s" % (im, og, ik, ak, ya)
        prayer_day_key = key
        last_prayer_sync = time.ticks_ms()
        return True
    except Exception:
        return False


def _prayer_minutes(t):
    try:
        return int(t[0:2]) * 60 + int(t[3:5])
    except Exception:
        return -1


def _nearest_prayer_text(lt):
    now_min = lt[3] * 60 + lt[4]
    best = None
    for name, tm in prayer_times:
        m = _prayer_minutes(tm)
        if m >= now_min:
            best = (name, tm)
            break
    if best is None and prayer_times:
        best = prayer_times[-1]
    if best is None:
        return prayer_text
    return "%s %s" % (best[0], best[1])


def _all_prayer_text():
    if not prayer_times:
        return prayer_text
    gap = " " * (prayer_gap_idx + 1)
    out = ""
    for name, tm in prayer_times:
        if out:
            out += gap
        out += name + " " + tm
    return out


def _prayer_display_text(lt):
    if prayer_mode_idx == 0:
        return ""
    if not prayer_text:
        if is_online():
            return "NAMAZ ALINIYOR"
        if WIFI_SSID:
            return "NAMAZ ICIN WIFI?"
        return "NAMAZ ICIN WIFI BAGLA"
    if prayer_mode_idx == 1:
        return "YAKIN " + _nearest_prayer_text(lt)
    return _all_prayer_text()


def _hm_from_iso(s):

    try:
        if "T" in s:
            return s.split("T", 1)[1][:5]
        return s[:5]
    except Exception:
        return "--:--"


def _fmt_int(v):
    try:
        return str(int(float(v) + 0.5))
    except Exception:
        return "--"


# ===================== DURUM =====================
wlan = None
ntp_ok = False
last_ntp = 0
spi = None
lcd = None
touch = None
bl_pwm = None

prev_t = ["", "", "", ""]
last_sec = -1
last_day = -1
colon_on = True
_digital_colon_level_prev = -1
_seconds_fill_prev = -1

prayer_text = ""
prayer_times = []
prayer_day_key = ""
last_prayer_sync = 0

WATCHDOG_STALE_MS = 90000
OTA_BOOT_STABLE_MS = 15000
_watchdog = None
_watchdog_timer = None
_watchdog_heartbeat = 0
_ota_boot_confirmed = False
WEATHER_REFRESH_MS = 30 * 60 * 1000
WEATHER_RETRY_MS = 5 * 60 * 1000
_weather_cache_days = []
_weather_cache_ms = 0
_weather_last_attempt = 0
_weather_cache_version = 0


def _watchdog_touch():
    global _watchdog_heartbeat
    _watchdog_heartbeat = time.ticks_ms()


def _watchdog_timer_step(_timer):
    try:
        if (_watchdog is not None and
                time.ticks_diff(time.ticks_ms(), _watchdog_heartbeat) <
                WATCHDOG_STALE_MS):
            _watchdog.feed()
    except Exception:
        pass


def watchdog_start():
    global _watchdog, _watchdog_timer
    _watchdog_touch()
    if WDT is None or Timer is None:
        return False
    try:
        _watchdog = WDT(timeout=8000)
        try:
            _watchdog_timer = Timer(-1)
        except Exception:
            _watchdog_timer = Timer()
        _watchdog_timer.init(period=1000, mode=Timer.PERIODIC,
                             callback=_watchdog_timer_step)
        _watchdog.feed()
        return True
    except Exception:
        _watchdog = None
        _watchdog_timer = None
        return False


def _ota_confirm_boot_if_stable(started, now):
    global _ota_boot_confirmed
    if (_ota_boot_confirmed or
            time.ticks_diff(now, started) < OTA_BOOT_STABLE_MS):
        return
    try:
        os.stat("ota_pending.txt")
    except Exception:
        _ota_boot_confirmed = True
        return
    for path in ("ota_pending.txt", "ota_booting.txt"):
        try:
            os.remove(path)
        except Exception:
            pass
    for name in ("main.py", "clock_app.py", "gpt_stream.py",
                 "sor_feature.py", "ota_feature.py", "ota_release.txt"):
        try:
            os.remove(".bak_" + name)
        except Exception:
            pass
    _ota_boot_confirmed = True


def show_status_screen(msg, color=AMBER):
    lcd.fill(BG)
    x = (WIDTH - len(msg) * 6) // 2
    if x < 2:
        x = 2
    lcd.text(msg, x, HEIGHT // 2 - 4, color, 1)


_gpt_wait_active = False
_gpt_wait_phase = 0
_gpt_wait_last = 0
_GPT_WAIT_HEIGHTS = (8, 14, 22, 14)
_GPT_WAIT_X = 6
_GPT_WAIT_Y = 6
_GPT_WAIT_W = 48
_GPT_WAIT_H = 34
_GPT_WAIT_INTERVAL_MS = 140
_wifi_wait_phase = 0
_wifi_wait_last = 0
_WIFI_WAIT_HEIGHTS = (4, 7, 12, 7)
_WIFI_WAIT_INTERVAL_MS = 140


def _gpt_wait_bar(x, height):
    top = _GPT_WAIT_Y + (_GPT_WAIT_H - height) // 2
    lcd.fill_rect(x + 1, top, 4, height, TITLE_COL)
    if height > 4:
        lcd.fill_rect(x, top + 2, 6, height - 4, TITLE_COL)


def _gpt_wait_step(force=False):
    global _gpt_wait_phase, _gpt_wait_last
    if not _gpt_wait_active or lcd is None:
        return
    _watchdog_touch()
    now = time.ticks_ms()
    if (not force and
            time.ticks_diff(now, _gpt_wait_last) < _GPT_WAIT_INTERVAL_MS):
        return
    _gpt_wait_last = now
    lcd.fill_rect(_GPT_WAIT_X, _GPT_WAIT_Y, _GPT_WAIT_W, _GPT_WAIT_H, BG)
    phase = (-(_gpt_wait_phase // 2)) % 4
    next_phase = (phase - 1) % 4
    between = _gpt_wait_phase & 1
    for i in range(4):
        height = _GPT_WAIT_HEIGHTS[(phase + i) % 4]
        if between:
            next_height = _GPT_WAIT_HEIGHTS[(next_phase + i) % 4]
            height = (height + next_height) // 2
        _gpt_wait_bar(_GPT_WAIT_X + 4 + i * 10, height)
    _gpt_wait_phase = (_gpt_wait_phase + 1) % 8


def _gpt_wait_start():
    global _gpt_wait_active, _gpt_wait_phase, _gpt_wait_last
    _gpt_wait_active = True
    _gpt_wait_phase = 0
    _gpt_wait_last = 0
    if lcd is not None:
        lcd.fill_rect(0, 0, WIDTH, ANS_TOP, BG)
    _gpt_wait_step(True)


def _gpt_wait_stop():
    global _gpt_wait_active
    _gpt_wait_active = False
    if lcd is not None:
        lcd.fill_rect(_GPT_WAIT_X, _GPT_WAIT_Y,
                      _GPT_WAIT_W, _GPT_WAIT_H, BG)
    gc.collect()


def _wifi_wait_step(force=False):
    global _wifi_wait_phase, _wifi_wait_last
    if lcd is None or not WIFI_SSID:
        return
    _watchdog_touch()
    now = time.ticks_ms()
    if (not force and
            time.ticks_diff(now, _wifi_wait_last) < _WIFI_WAIT_INTERVAL_MS):
        return
    if is_online():
        return
    _wifi_wait_last = now
    lcd.fill_rect(0, 0, 48, 18, BG)
    phase = (-(_wifi_wait_phase // 2)) % 4
    next_phase = (phase - 1) % 4
    between = _wifi_wait_phase & 1
    for i in range(4):
        height = _WIFI_WAIT_HEIGHTS[(phase + i) % 4]
        if between:
            next_height = _WIFI_WAIT_HEIGHTS[(next_phase + i) % 4]
            height = (height + next_height) // 2
        top = 2 + (14 - height) // 2
        lcd.fill_rect(4 + i * 10, top, 6, height, TITLE_COL)
    _wifi_wait_phase = (_wifi_wait_phase + 1) % 8


# ===================== WIFI DOSYA / TARAMA =====================
WIFI_FILE = "wifi.txt"
KNOWN_FILE = "wifi_known.txt"


def load_known():
    d = {}
    try:
        f = open(KNOWN_FILE)
        data = f.read()
        f.close()
        for line in data.split("\n"):
            if "\t" in line:
                a, b = line.split("\t", 1)
                if a:
                    d[a] = b
    except Exception:
        pass
    return d


def save_known(ssid, pw):
    d = load_known()
    d[ssid] = pw
    data = ""
    for k in d:
        data += k + "\t" + d[k] + "\n"
    safe_write_text(KNOWN_FILE, data)


def known_get(ssid):
    return load_known().get(ssid, None)


def load_wifi():
    global WIFI_SSID, WIFI_PASS
    try:
        f = open(WIFI_FILE)
        data = f.read()
        f.close()
        parts = data.split("\n")
        if len(parts) >= 2 and parts[0]:
            WIFI_SSID = parts[0]
            WIFI_PASS = parts[1]
            return True
    except Exception:
        pass
    return False


def save_wifi(ssid, pw):
    safe_write_text(WIFI_FILE, ssid + "\n" + pw + "\n")


def scan_networks():
    if network is None:
        return []
    try:
        w = network.WLAN(network.STA_IF)
        w.active(True)
        raw = w.scan()
    except Exception:
        return []
    best = {}
    for n in raw:
        try:
            s = n[0]
            ssid = s.decode() if isinstance(s, (bytes, bytearray)) else str(s)
        except Exception:
            ssid = ""
        if ssid == "":
            continue
        rssi = n[3] if len(n) > 3 else -100
        if ssid not in best or rssi > best[ssid]:
            best[ssid] = rssi
    items = list(best.keys())
    items.sort(key=lambda s: best[s], reverse=True)
    return items[:18]


# ===================== EKRAN KLAVYESI =====================
KB_TOP = 80
KEY_H = 30
IN_X = 4
IN_Y = 24
IN_CW = 6
IN_CH = 11
IN_CPL = (WIDTH - 8) // IN_CW

LOW_ROWS = ["1234567890", "qwertyuiop", "asdfghjkl", "zxcvbnm"]
UP_ROWS = ["1234567890", "QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
SYM_ROWS = ["1234567890", "@#$%&*-_+=", "!?.,:;/'()"]


def in_pos(idx):
    return IN_X + (idx % IN_CPL) * IN_CW, IN_Y + (idx // IN_CPL) * IN_CH


def in_char_at(idx, ch):
    x, y = in_pos(idx)
    if y > KB_TOP - 12:
        return
    lcd.text(ch, x, y, FG, 1)


def in_erase_at(idx):
    x, y = in_pos(idx)
    if y > KB_TOP - 12:
        return
    lcd.fill_rect(x, y, IN_CW, IN_CH, BG)


def in_draw_all(text):
    for i in range(len(text)):
        in_char_at(i, text[i])


def _kb_build(mode):
    rows = SYM_ROWS if mode == "sym" else (UP_ROWS if mode == "up" else LOW_ROWS)
    keys = []
    for ri in range(len(rows)):
        rowstr = rows[ri]
        n = len(rowstr)
        kw = 32
        sx = (WIDTH - n * kw) // 2
        y = KB_TOP + ri * (KEY_H + 2)
        for ci in range(n):
            x = sx + ci * kw
            keys.append({"label": rowstr[ci], "x": x, "y": y, "w": kw - 2,
                         "h": KEY_H, "kind": "char", "val": rowstr[ci]})
    y = KB_TOP + 4 * (KEY_H + 2)
    if mode == "sym":
        keys.append({"label": "ABC", "x": 0, "y": y, "w": 52, "h": KEY_H, "kind": "toletters"})
        keys.append({"label": "SIL", "x": 56, "y": y, "w": 52, "h": KEY_H, "kind": "back"})
        keys.append({"label": "BOSLUK", "x": 112, "y": y, "w": 80, "h": KEY_H, "kind": "space"})
        keys.append({"label": "TAMAM", "x": 196, "y": y, "w": 124, "h": KEY_H, "kind": "send"})
    else:
        case_label = "ABC" if mode == "low" else "abc"
        keys.append({"label": case_label, "x": 0, "y": y, "w": 40, "h": KEY_H, "kind": "case"})
        keys.append({"label": "#@", "x": 44, "y": y, "w": 40, "h": KEY_H, "kind": "sym"})
        keys.append({"label": "SIL", "x": 88, "y": y, "w": 48, "h": KEY_H, "kind": "back"})
        keys.append({"label": "BOSLUK", "x": 140, "y": y, "w": 76, "h": KEY_H, "kind": "space"})
        keys.append({"label": "TAMAM", "x": 220, "y": y, "w": 100, "h": KEY_H, "kind": "send"})
    return keys


def _kb_key_draw(k, pressed=False):
    if pressed:
        bg = FG; fg = BG
    else:
        bg = DARKGRAY; fg = WHITE
        if k["kind"] == "send":
            bg = GREEN; fg = BLACK
        elif k["kind"] == "geri":
            bg = BLUE; fg = WHITE
        elif k["kind"] in ("back", "case", "sym", "toletters"):
            bg = GRAY
    x, y, w, h = k["x"], k["y"], k["w"], k["h"]
    lbl = k["label"]
    _draw_round_button(x, y, w, h, GRAY, bg, lbl, fg)


def _kb_draw(keys):
    lcd.fill_rect(0, KB_TOP - 2, WIDTH, HEIGHT - (KB_TOP - 2), BG)
    for k in keys:
        _kb_key_draw(k, False)


def _entry_labels(title, show_ayar=False):
    lcd.fill_rect(0, 0, WIDTH, IN_Y - 2, BG)
    lcd.text(title, 4, 4, TITLE_COL, 1)
    if show_ayar:
        lcd.fill_rect(206, 2, 52, 16, DARKGRAY)
        lcd.rect(206, 2, 52, 16, WHITE)
        lcd.text("AYAR", 216, 6, WHITE, 1)
    lcd.fill_rect(264, 2, 54, 16, BLUE)
    lcd.rect(264, 2, 54, 16, WHITE)
    lcd.text("GERI", 274, 6, WHITE, 1)


def run_text_entry(title, initial="", on_ayar=None):
    text = initial
    mode = "low"
    keys = _kb_build(mode)
    show_ayar = on_ayar is not None
    lcd.fill(BG)
    _entry_labels(title, show_ayar)
    _kb_draw(keys)
    in_draw_all(text)
    last = 0
    while True:
        res = touch.read_screen()
        if res is None:
            time.sleep_ms(20)
            continue
        raw_x, raw_y, x, y = res
        now = time.ticks_ms()
        if time.ticks_diff(now, last) < TOUCH_DEBOUNCE_MS:
            continue
        last = now
        if x >= 262 and y <= 20:
            return None
        if show_ayar and 204 <= x <= 260 and y <= 20:
            on_ayar()
            lcd.fill(BG)
            _entry_labels(title, show_ayar)
            _kb_draw(keys)
            in_draw_all(text)
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
        if kind == "char":
            if len(text) < 64:
                idx = len(text)
                text += k["val"]
                in_char_at(idx, k["val"])
        elif kind == "space":
            if len(text) < 64:
                text += " "
        elif kind == "back":
            if text:
                idx = len(text) - 1
                text = text[:-1]
                in_erase_at(idx)
        elif kind == "case":
            mode = "up" if mode == "low" else "low"
            keys = _kb_build(mode)
            _kb_draw(keys)
        elif kind == "sym":
            mode = "sym"
            keys = _kb_build(mode)
            _kb_draw(keys)
        elif kind == "toletters":
            mode = "low"
            keys = _kb_build(mode)
            _kb_draw(keys)
        elif kind == "send":
            return text


# ===================== WIFI SECME / BAGLANMA =====================
def draw_lock(x, y, closed, col):
    by = y + 3
    lcd.fill_rect(x, by, 8, 6, col)
    lcd.fill_rect(x + 3, by + 2, 2, 2, BG)
    lcd.hline(x + 1, y, 6, col)
    lcd.vline(x + 1, y, by - y, col)
    if closed:
        lcd.vline(x + 6, y, by - y, col)
    else:
        lcd.vline(x + 6, y, (by - y) - 2, col)


def run_wifi_pick():
    while True:
        show_status_screen("AGLAR TARANIYOR...", TITLE_COL)
        nets = scan_networks()
        known = load_known()
        lcd.fill(BG)
        lcd.text("WIFI SEC", 4, 4, TITLE_COL, 1)
        rows = []
        y = 22
        for s in nets:
            disp = s if len(s) <= 44 else s[:44]
            lcd.text(disp, 8, y, FG, 1)
            if s in known:
                draw_lock(305, y - 1, False, GREEN)
            else:
                draw_lock(305, y - 1, True, LOCK_CLOSED_COL)
            rows.append((y - 4, y + 12, s))
            y += 18
            if y > 184:
                break


        if mode_idx == 1:
            tara_bg = ellegir_bg = geri_bg = BLACK
        else:
            tara_bg = DARKGRAY
            ellegir_bg = BLUE
            geri_bg = GRAY
        b0, b1, b2 = 107, 106, 107
        lcd.fill_rect(0, 210, b0, 30, tara_bg)
        lcd.rect(0, 210, b0, 30, GRAY)
        lcd.text("TARA", 34, 220, WHITE, 1)
        lcd.fill_rect(b0, 210, b1, 30, ellegir_bg)
        lcd.rect(b0, 210, b1, 30, GRAY)
        lcd.text("ELLE GIR", b0 + 22, 220, WHITE, 1)
        lcd.fill_rect(b0 + b1, 210, b2, 30, geri_bg)
        lcd.rect(b0 + b1, 210, b2, 30, GRAY)
        lcd.text("GERI", b0 + b1 + 32, 220, WHITE, 1)

        last = 0
        while True:
            res = touch.read_screen()
            if res is None:
                time.sleep_ms(20)
                continue
            raw_x, raw_y, x, y2 = res
            now = time.ticks_ms()
            if time.ticks_diff(now, last) < TOUCH_DEBOUNCE_MS:
                continue
            last = now
            if y2 >= 210:
                if x < b0:
                    break
                elif x < b0 + b1:
                    return ""
                else:
                    return None
            else:
                for (y0, y1, s) in rows:
                    if y0 <= y2 <= y1:
                        lcd.fill_rect(2, y0, WIDTH - 4, y1 - y0, BLUE)
                        disp = s if len(s) <= 44 else s[:44]
                        lcd.text(disp, 8, y0 + 4, WHITE, 1)
                        time.sleep_ms(400)
                        return s


def ntp_sync():
    global ntp_ok, last_ntp
    if ntptime is None or rtc is None:
        return False
    try:
        ntptime.settime()
        secs = time.time() + TZ_OFFSET * 3600
        tm = time.localtime(secs)
        rtc.datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))
        ntp_ok = True
        last_ntp = time.ticks_ms()
        return True
    except Exception:
        return False


def wifi_connect(ssid, pw, timeout=12000, progress=None):
    if network is None:
        return False
    try:
        w = network.WLAN(network.STA_IF)
        w.active(True)
        if not w.isconnected():
            w.connect(ssid, pw)
            t0 = time.ticks_ms()
            while not w.isconnected():
                if time.ticks_diff(time.ticks_ms(), t0) > timeout:
                    return False
                if progress is not None:
                    progress()
                time.sleep_ms(100)
        return w.isconnected()
    except Exception:
        return False


def wifi_reconnect_start(ssid, pw):
    """Ana donguyu bekletmeden WiFi baglanti denemesini baslatir."""
    if network is None:
        return False
    try:
        w = network.WLAN(network.STA_IF)
        w.active(True)
        if not w.isconnected():
            w.connect(ssid, pw)
        return True
    except Exception:
        return False


def wifi_boot_connect():
    """Acilis animasyonu surerken en fazla uc WiFi denemesi yapar."""
    if not WIFI_SSID or network is None:
        return 0
    attempts = 0
    for attempt in range(WIFI_BOOT_RETRY_COUNT):
        attempts = attempt + 1
        if wifi_connect(WIFI_SSID, WIFI_PASS,
                        WIFI_BOOT_CONNECT_TIMEOUT_MS, boot_wait_tick):
            return attempts
        try:
            network.WLAN(network.STA_IF).disconnect()
        except Exception:
            pass
        time.sleep_ms(120)
    return attempts


def run_wifi_setup():
    global WIFI_SSID, WIFI_PASS
    ssid = run_wifi_pick()
    if ssid is None:
        return
    if ssid == "":
        ssid = run_text_entry("AG ADI:", "")
        if not ssid:
            return
    kp = known_get(ssid)
    if kp is not None:
        pw = kp
    else:
        pw = run_text_entry("SIFRE:", "")
        if pw is None:
            return
    WIFI_SSID = ssid
    WIFI_PASS = pw
    show_status_screen("BAGLANIYOR...", AMBER)
    if wifi_connect(WIFI_SSID, WIFI_PASS):
        save_wifi(WIFI_SSID, WIFI_PASS)
        save_known(WIFI_SSID, WIFI_PASS)
        show_status_screen("BAGLANDI, SAAT ALINIYOR", GREEN)
        ntp_sync()
        geo_locate()
        prayer_sync()
        sunset_sync()
        show_status_screen("TAMAM: " + ssid[:16], GREEN)
    else:
        show_status_screen("OLMADI, SIFREYI KONTROL ET", RED)
    time.sleep_ms(1400)


# ===================== 7-SEGMENT SAAT =====================
SEG_MAP = {
    "0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg",
    "4": "bcfg", "5": "acdfg", "6": "acdefg", "7": "abc",
    "8": "abcdefg", "9": "abcdfg", " ": "",
}

DW = 52; DH = 96; DT = 10
TIME_Y = 34
DIGIT_X = [32, 90, 178, 236]
COLONX = 148; COLONW = 24

BAR_X = 32; BAR_Y = 138; BAR_W = 256; BAR_H = 5
DATE_Y1 = 150; DATE_Y2 = 176
BTN_Y = 212; BTN_H = 28

def _digital_layout():


    return (24, 58, 108, 11, [18, 82, 181, 245], 146, 28,
            22, 148, 276, 6, 166, 196)


def _seg_rects(x, y, W, H, T):
    mid = y + (H - T) // 2
    return {
        "a": (x + T, y, W - 2 * T, T),
        "g": (x + T, mid, W - 2 * T, T),
        "d": (x + T, y + H - T, W - 2 * T, T),
        "f": (x, y + T, T, mid - (y + T)),
        "b": (x + W - T, y + T, T, mid - (y + T)),
        "e": (x, mid + T, T, (y + H - T) - (mid + T)),
        "c": (x + W - T, mid + T, T, (y + H - T) - (mid + T)),
    }


def draw_seg_digit(x, ch):
    color = FG
    ty, dw, dh, dt, _dx, _cx, _cw, _bx, _by, _bw, _bh, _dy1, _dy2 = _digital_layout()
    rects = _seg_rects(x, ty, dw, dh, dt)
    lcd.fill_rect(x, ty, dw, dh, BG)
    for s in "abcdefg":
        r = rects[s]
        lcd.fill_rect(r[0], r[1], r[2], r[3], FG_DIM)
    for s in SEG_MAP.get(ch, ""):
        r = rects[s]
        lcd.fill_rect(r[0], r[1], r[2], r[3], color)


def time_string(lt):
    hh = lt[3]; mm = lt[4]
    if USE_24H:
        hs = "%02d" % hh
    else:
        h12 = hh % 12
        if h12 == 0:
            h12 = 12
        hs = "%2d" % h12
    return hs + ("%02d" % mm)


def draw_time(lt, force=False):
    s = time_string(lt)
    _ty, _dw, _dh, _dt, dxs, _cx, _cw, _bx, _by, _bw, _bh, _dy1, _dy2 = _digital_layout()
    for i in range(4):
        if force or s[i] != prev_t[i]:
            draw_seg_digit(dxs[i], s[i])
            prev_t[i] = s[i]


def draw_colon(on):
    ty, _dw, dh, _dt, _dx, cx0, cw, _bx, _by, _bw, _bh, _dy1, _dy2 = _digital_layout()
    cx = cx0 + cw // 2
    lcd.fill_rect(cx - 7, ty, 15, dh, BG)
    if on:
        col = FG
        lcd.circle(cx, ty + dh // 3, 6, col)
        lcd.circle(cx, ty + 2 * dh // 3, 6, col)


def draw_seconds(sec):
    _ty, _dw, _dh, _dt, _dx, _cx, _cw, bx, by, bw, bh, _dy1, _dy2 = _digital_layout()
    fill = (sec + 1) * bw // 60
    if fill > 0:
        lcd.fill_rect(bx, by, fill, bh, FG)
    if fill < bw:
        lcd.fill_rect(bx + fill, by, bw - fill, bh, FG_DIM)


def draw_date(lt):
    _ty, _dw, _dh, _dt, _dx, _cx, _cw, _bx, _by, _bw, _bh, dy1, dy2 = _digital_layout()
    wd = GUNLER[lt[6]] if 0 <= lt[6] < 7 else ""
    ds = "%d %s %d" % (lt[2], AYLAR[(lt[1] - 1) % 12], lt[0])
    lcd.fill_rect(0, dy1, WIDTH, 36, BG)
    lcd.text(wd, (WIDTH - len(wd) * 12) // 2, dy1, FG, 2)
    lcd.text(ds, (WIDTH - len(ds) * 12) // 2, dy2, GRAY, 2)


def _scaled_text_width(txt, style):
    glyph_w, _glyph_h, advance = style
    return 0 if not txt else (len(txt) - 1) * advance + glyph_w


def _draw_scaled_text(txt, x, y, color, style):
    glyph_w, glyph_h, advance = style
    for ch in txt:
        data = FONT[ch] if ch in FONT else FONT.get(ch.upper(), FONT[" "])
        for dy in range(glyph_h):
            bits = data[dy * 7 // glyph_h]
            dx = 0
            while dx < glyph_w:
                src_x = dx * 5 // glyph_w
                if bits[src_x] == "1":
                    lcd.fill_rect(x + dx, y + dy, 1, 1, color)
                dx += 1
        x += advance


def _prayer_text_style(txt, max_width):
    idx = prayer_size_idx
    while idx > 0 and _scaled_text_width(txt, PRAYER_SIZE_STYLES[idx]) > max_width:
        idx -= 1
    return PRAYER_SIZE_STYLES[idx]


OTA_TOP_TXT = "OTA"
OTA_TOP_W = len(OTA_TOP_TXT) * 6
OTA_TOP_X = WIDTH - OTA_TOP_W - 4
OTA_TOP_HIT_X0 = OTA_TOP_X - 10
ota_update_available = False
ota_available_version = ""

TOPBTN_TXT = "MANUEL"
TOPBTN_W = len(TOPBTN_TXT) * 6
TOPBTN_X = OTA_TOP_X - TOPBTN_W - 12
TOPBTN_HIT_X0 = TOPBTN_X - 10


def _ota_version_parts(value):
    parts = []
    for item in str(value).split("."):
        digits = ""
        for ch in item:
            if "0" <= ch <= "9":
                digits += ch
            else:
                break
        parts.append(int(digits) if digits else 0)
    while len(parts) < 4:
        parts.append(0)
    return tuple(parts[:4])


def _ota_check_available():
    """Manifesti kontrol et; ag hatasinda mevcut bildirimi silme."""
    global ota_update_available, ota_available_version
    try:
        status, text = https_get(
            "raw.githubusercontent.com",
            "/ysnkrt/masa-saati-ota/main/ota.json", 20)
        if status != 200 or not text:
            return ota_update_available
        manifest = json.loads(text)
        version = str(manifest.get("version", "")).strip()
        remote_release = str(manifest.get("release_id", "")).strip()
        local_release = ""
        try:
            f = open(OTA_RELEASE_FILE)
            local_release = f.read().strip()
            f.close()
        except Exception:
            pass
        if remote_release:
            ota_update_available = remote_release != local_release
        else:
            ota_update_available = bool(
                version and _ota_version_parts(version) >
                _ota_version_parts(APP_VERSION))
        ota_available_version = version if ota_update_available else ""
    except Exception:
        pass
    return ota_update_available


def _run_ota_from_top():
    if not is_online():
        show_status_screen("OTA ICIN WIFI GEREKLI", AMBER)
        time.sleep_ms(1400)
        return
    updater = None
    try:
        import ota_feature as updater
    except Exception:
        pass
    if updater is not None:
        updater.run(sys.modules[__name__])
        return
    _ota_check_available()
    version = (" v" + ota_available_version) if ota_available_version else ""
    if ota_update_available:
        show_status_screen("YENI SURUM" + version, GREEN)
    else:
        show_status_screen("SURUM GUNCEL: v" + APP_VERSION, GREEN)
    time.sleep_ms(1600)


def draw_status():


    lcd.fill_rect(0, 0, WIDTH, 18, BG)
    online = is_online()
    lcd.text(OTA_TOP_TXT, OTA_TOP_X, 3, GREEN if online else GRAY, 1)
    if online:
        return
    lt = time.localtime()
    if WIFI_SSID:
        _wifi_wait_step(True)
    elif ntp_ok:
        lcd.text("NTP", 4, 3, GREEN, 1)
    else:
        lcd.text("AYAR'DAN KUR", 4, 3, GRAY, 1)

    if not USE_24H:
        ap = "OO" if lt[3] < 12 else "OS"
        lcd.text(ap, TOPBTN_X - 18, 3, GRAY, 1)
    lcd.text(TOPBTN_TXT, TOPBTN_X, 3, FG, 1)


def draw_bottom():
    lcd.fill_rect(0, BTN_Y, WIDTH, BTN_H, BG)

    lcd.hline(0, BTN_Y, WIDTH, GRAY)
    labels = ("AYARLAR", "HAVA", "GPT")
    q = WIDTH // len(labels)
    for i, lbl in enumerate(labels):
        if i:
            lcd.vline(q * i, BTN_Y, BTN_H, GRAY)
        x0 = q * i
        lcd.text(lbl, x0 + (q - len(lbl) * 12) // 2, BTN_Y + 7, FG, 2)


def digital_static():
    global prev_t, _digital_colon_level_prev, _seconds_fill_prev
    prev_t = ["", "", "", ""]
    _digital_colon_level_prev = -1
    _seconds_fill_prev = -1
    lt = time.localtime()
    draw_time(lt, True)
    if anim_on:
        draw_colon_level(6)
    else:
        draw_colon(colon_on)
    draw_seconds_f(lt[5] / 60.0)
    draw_date(lt)


def digital_update(lt, day_changed):
    draw_time(lt)
    if anim_on:
        draw_colon_level(6)
    else:
        draw_colon(colon_on)
    draw_seconds_f(lt[5] / 60.0)
    if day_changed:
        draw_date(lt)


# ============================================================
# ---- MODEL 1: ANALOG ----


# ============================================================
AN_CX = 160
AN_CY = 102
AN_R = 90
AN_TICKS = 60
AN_TICK_LEN = 16
_PI = 3.14159265

_an_last_fill = -1
_an_last_min = -1
_an_date_prev = ""
_an_prayer_prev = ""


AN_PR_X = 2
AN_PR_Y = 22
AN_PR_W = 66
AN_PR_H = 166


def _an_tick_geom(i):

    a = i * (2.0 * _PI / AN_TICKS)
    s = math.sin(a)
    c = math.cos(a)
    outer = AN_R - 3
    inner = outer - AN_TICK_LEN
    x0 = AN_CX + int(inner * s)
    y0 = AN_CY - int(inner * c)
    x1 = AN_CX + int(outer * s)
    y1 = AN_CY - int(outer * c)
    return x0, y0, x1, y1


def _an_draw_tick(i, color):


    x0, y0, x1, y1 = _an_tick_geom(i)
    lcd.line(x0, y0, x1, y1, color)
    a = i * (2.0 * _PI / AN_TICKS)
    ox = 1 if math.cos(a) >= 0 else -1
    oy = 1 if math.sin(a) >= 0 else -1
    lcd.line(x0 + ox, y0, x1 + ox, y1, color)
    lcd.line(x0, y0 + oy, x1, y1 + oy, color)


def analog_tick_ring(filled):


    for i in range(AN_TICKS):
        _an_draw_tick(i, RING_FULL if i < filled else RING_EMPTY)


def _an_fill_from_sec(sec):

    if sec > AN_TICKS:
        sec = AN_TICKS
    return sec


def _analog_prayer_key(lt):

    return (_prayer_display_text(lt) + "|" + str(prayer_mode_idx) + "|" +
            str(prayer_thick_idx) + "|" + str(prayer_gap_idx) + "|" +
            str(mode_idx) + "|" + str(_weather_cache_version))


def analog_weather_mini():
    y0 = AN_PR_Y + 88
    h = 19
    lcd.fill_rect(AN_PR_X, y0, AN_PR_W, AN_PR_H - 88, BG)
    if not _weather_cache_days:
        lcd.rect(AN_PR_X, y0, AN_PR_W, h, GRAY)
        lcd.text("HAVA --", AN_PR_X + 12, y0 + 6, GRAY, 1)
        return
    day = _weather_cache_days[0]
    current = _forecast_number(day.get("current"), "C")
    hi = _forecast_number(day.get("high"))
    low = _forecast_number(day.get("low"))
    rows = (
        ("ISI", current + " " + hi + "/" + low),
        ("YAG", "%" + _forecast_number(day.get("rain"))),
        ("R/G", _forecast_number(day.get("wind")) + "/" +
         _forecast_number(day.get("gust"))),
        ("D/B", day.get("sunrise", "--:--") + "/" +
         day.get("sunset", "--:--")),
    )
    for index, (title, value) in enumerate(rows):
        y = y0 + index * h
        lcd.fill_rect(AN_PR_X, y, AN_PR_W, h, DARKGRAY)
        lcd.rect(AN_PR_X, y, AN_PR_W, h, GRAY)
        lcd.text(title, AN_PR_X + 2, y + 2, TITLE_COL, 1)
        if len(value) * 6 <= AN_PR_W - 4:
            lcd.text(value, AN_PR_X + AN_PR_W - len(value) * 6 - 2,
                     y + 10, FG, 1)
        else:
            lcd.text(value[:11], AN_PR_X, y + 10, FG, 1)


def analog_prayer_panel(lt, force=False):


    global _an_prayer_prev
    key = _analog_prayer_key(lt)
    if not force and key == _an_prayer_prev:
        return
    _an_prayer_prev = key
    lcd.fill_rect(AN_PR_X, AN_PR_Y, AN_PR_W, AN_PR_H, BG)
    if prayer_mode_idx == 0:
        analog_weather_mini()
        return
    head = FG
    val = FG

    if not prayer_text:

        lcd.text("NAMAZ", AN_PR_X + 4, AN_PR_Y + 12, head, 1)
        if is_online():
            lcd.text("ALINIYOR", AN_PR_X + 2, AN_PR_Y + 28, GRAY, 1)
        elif WIFI_SSID:
            lcd.text("WIFI?", AN_PR_X + 6, AN_PR_Y + 28, GRAY, 1)
        else:
            lcd.text("WIFI", AN_PR_X + 8, AN_PR_Y + 28, GRAY, 1)
            lcd.text("YOK", AN_PR_X + 10, AN_PR_Y + 42, GRAY, 1)
        analog_weather_mini()
        return

    if prayer_mode_idx == 1:

        near = _nearest_prayer_text(lt)
        parts = near.split(" ")
        name = parts[0] if parts else "--"
        tm = parts[1] if len(parts) > 1 else "--:--"
        lcd.text("YAKIN", AN_PR_X + 4, AN_PR_Y + 10, head, 1)
        name_style = _prayer_text_style(name, AN_PR_W - 8)
        time_style = _prayer_text_style(tm, AN_PR_W - 8)
        name_x = AN_PR_X + (AN_PR_W - _scaled_text_width(name, name_style)) // 2
        time_x = AN_PR_X + (AN_PR_W - _scaled_text_width(tm, time_style)) // 2
        _draw_scaled_text(name, name_x, AN_PR_Y + 30, val, name_style)
        _draw_scaled_text(tm, time_x, AN_PR_Y + 50, val, time_style)
        analog_weather_mini()
        return


    lcd.text("NAMAZ", AN_PR_X + 4, AN_PR_Y + 2, head, 1)
    y = AN_PR_Y + 18
    for name, tm in prayer_times:
        text = name + " " + tm
        if y + 8 > AN_PR_Y + 84:
            break
        lcd.text(text, AN_PR_X + 3, y, val, 1)
        y += 13
    analog_weather_mini()


def analog_center_time(lt, force=False):

    global _an_last_min
    if not force and lt[4] == _an_last_min:
        return
    _an_last_min = lt[4]

    if USE_24H:
        hs = "%02d" % lt[3]
    else:
        h = lt[3] % 12
        if h == 0:
            h = 12
        hs = "%02d" % h
    s = hs + ":" + ("%02d" % lt[4])

    col = FG
    size = 4
    adv = 6 * size
    char_w = 5 * size
    th = 7 * size

    tw = (len(s) - 1) * adv + char_w
    startx = AN_CX - tw // 2
    starty = AN_CY - th // 2


    lcd.fill_rect(startx - 4, starty - 4, tw + 8, th + 8, BG)
    for i, ch in enumerate(s):
        lcd.text(ch, startx + i * adv, starty, col, size)


def analog_center_date(lt, force=False):

    global _an_date_prev
    wd = GUNLER[lt[6]] if 0 <= lt[6] < 7 else ""
    ds = "%02d.%02d.%d %s" % (lt[2], lt[1], lt[0], wd)
    if not force and ds == _an_date_prev:
        return
    _an_date_prev = ds
    y = AN_CY + AN_R + 6
    if y > BTN_Y - 12:
        y = BTN_Y - 12
    lcd.fill_rect(0, y, WIDTH, 10, BG)
    lcd.text(ds, (WIDTH - len(ds) * 6) // 2, y, GRAY, 1)


def analog_static():
    global _an_last_fill, _an_last_min, _an_date_prev, _an_prayer_prev
    _an_last_min = -1
    _an_date_prev = ""
    _an_prayer_prev = ""

    lcd.fill_rect(0, 16, WIDTH, BTN_Y - 16, BG)

    lt = time.localtime()
    fill = _an_fill_from_sec(lt[5])
    _an_last_fill = fill

    analog_tick_ring(fill)

    analog_center_time(lt, True)

    analog_center_date(lt, True)

    analog_prayer_panel(lt, True)


def analog_update(lt, day_changed):
    global _an_last_fill
    fill = _an_fill_from_sec(lt[5])
    if fill != _an_last_fill:
        if fill < _an_last_fill:

            analog_tick_ring(fill)
        else:

            for i in range(_an_last_fill, fill):
                _an_draw_tick(i, RING_FULL)
        _an_last_fill = fill


    analog_center_time(lt)

    analog_prayer_panel(lt)
    if day_changed:
        analog_center_date(lt)


# ---- MODEL 2: BUYUK YAZI (HH:MM:SS) ----
BIG_SIZE = 6
BIG_Y = 64
_big_prev = ""
_big_colon_level_prev = -1


def big_time_str(lt):
    if USE_24H:
        hs = "%02d" % lt[3]
    else:
        h = lt[3] % 12
        if h == 0:
            h = 12
        hs = "%2d" % h
    return hs + ":" + ("%02d" % lt[4]) + ":" + ("%02d" % lt[5])


def big_date(lt):
    wd = GUNLER[lt[6]] if 0 <= lt[6] < 7 else ""
    ds = "%d %s %d" % (lt[2], AYLAR[(lt[1] - 1) % 12], lt[0])
    lcd.fill_rect(0, 150, WIDTH, 40, BG)
    lcd.text(wd, (WIDTH - len(wd) * 12) // 2, 150, FG, 2)
    lcd.text(ds, (WIDTH - len(ds) * 12) // 2, 176, GRAY, 2)


def big_update(lt, force=False):
    global _big_prev
    s = big_time_str(lt)
    adv = BIG_SIZE * 6
    startx = (WIDTH - len(s) * adv) // 2
    col = FG
    for i in range(len(s)):
        if force or i >= len(_big_prev) or s[i] != _big_prev[i]:
            cx = startx + i * adv
            lcd.fill_rect(cx, BIG_Y, adv, BIG_SIZE * 7, BG)
            lcd.text(s[i], cx, BIG_Y, col, BIG_SIZE)
    _big_prev = s


def big_static():
    global _big_prev, _big_colon_level_prev
    _big_prev = ""
    _big_colon_level_prev = -1
    lcd.fill_rect(0, 16, WIDTH, BTN_Y - 16, BG)
    lt = time.localtime()
    big_update(lt, True)
    big_date(lt)


# ============================================================
# ---- MODEL 3: NABIZ SAATI (dijital HH:MM + EKG dalgasi) ----


# ============================================================
PULSE_SIZE = 5
PULSE_Y = 90
_padv = PULSE_SIZE * 6
_ptw_max = 4 * _padv + 5 * PULSE_SIZE

BAR_W2 = 8
BAR_STEP = 13
BAR_BUFFER = 10
BAR_CY = PULSE_Y + (PULSE_SIZE * 7) // 2
BAR_BASE_H = 6
BAR_MAX_H = 34
PULSE_BAR_TIERS = 5

_bar_inner_half = _ptw_max // 2 + BAR_BUFFER
LEFT_BAR_X = tuple(WIDTH // 2 - _bar_inner_half - t * BAR_STEP for t in range(PULSE_BAR_TIERS))
RIGHT_BAR_X = tuple(WIDTH // 2 + _bar_inner_half + t * BAR_STEP for t in range(PULSE_BAR_TIERS))

_pulse_prev = ""
_pulse_date_prev = ""
_pulse_colon_x = 0
_pulse_prev_h = [BAR_BASE_H] * (2 * PULSE_BAR_TIERS)
_pulse_colon_level_prev = -1


def _pulse_time_str(lt):


    if USE_24H:
        hs = "%02d" % lt[3]
    else:
        h = lt[3] % 12
        if h == 0:
            h = 12
        hs = str(h)
    return hs + ":" + ("%02d" % lt[4])


def pulse_time(lt, force=False):
    global _pulse_prev, _pulse_colon_x, _pulse_colon_level_prev
    s = _pulse_time_str(lt)
    if not force and s == _pulse_prev:
        return
    col = FG
    tw = (len(s) - 1) * _padv + 5 * PULSE_SIZE
    x0 = (WIDTH - tw) // 2
    lcd.fill_rect(0, PULSE_Y, WIDTH, PULSE_SIZE * 7, BG)
    ci = s.find(":")
    _pulse_colon_x = x0 + ci * _padv
    for i, ch in enumerate(s):
        if i == ci:
            continue
        lcd.text(ch, x0 + i * _padv, PULSE_Y, col, PULSE_SIZE)
    _pulse_prev = s
    _pulse_colon_level_prev = -1


def pulse_colon_level(level):
    global _pulse_colon_level_prev
    if level == _pulse_colon_level_prev:
        return
    _pulse_colon_level_prev = level
    cx = _pulse_colon_x
    lcd.fill_rect(cx, PULSE_Y, _padv, PULSE_SIZE * 7, BG)
    if level > 0:
        lcd.text(":", cx, PULSE_Y, _dim(FG, level, 6), PULSE_SIZE)


def _bar_height(tier, frac):

    delay = tier * 0.15
    lp = frac - delay
    if lp < 0.0 or lp > 0.4:
        return BAR_BASE_H
    x = lp / 0.4
    shape = 1.0 - abs(1.0 - 2.0 * x)
    return int(BAR_BASE_H + (BAR_MAX_H - BAR_BASE_H) * shape)


def pulse_bars(frac, force=False):
    global _pulse_prev_h
    col = FG
    positions = LEFT_BAR_X + RIGHT_BAR_X
    for i in range(len(positions)):
        tier = i % PULSE_BAR_TIERS
        h = _bar_height(tier, frac) if anim_on else BAR_BASE_H
        if not force and h == _pulse_prev_h[i]:
            continue
        x = positions[i]
        ey = BAR_CY - BAR_MAX_H // 2 - 1
        lcd.fill_rect(x - BAR_W2 // 2 - 1, ey, BAR_W2 + 2, BAR_MAX_H + 2, BG)
        y0 = BAR_CY - h // 2
        lcd.fill_rect(x - BAR_W2 // 2, y0, BAR_W2, h, col)
        _pulse_prev_h[i] = h


def pulse_date(lt, force=False):
    global _pulse_date_prev
    wd = GUNLER[lt[6]] if 0 <= lt[6] < 7 else ""
    ds = "%02d.%02d.%d %s" % (lt[2], lt[1], lt[0], wd)
    if not force and ds == _pulse_date_prev:
        return
    _pulse_date_prev = ds
    lcd.fill_rect(0, 196, WIDTH, 9, BG)
    lcd.text(ds, (WIDTH - len(ds) * 6) // 2, 196, DARKGRAY, 1)


def pulse_static():
    global _pulse_prev, _pulse_date_prev, _pulse_prev_h, _pulse_colon_level_prev
    _pulse_prev = ""
    _pulse_date_prev = ""
    _pulse_prev_h = [BAR_BASE_H] * (2 * PULSE_BAR_TIERS)
    _pulse_colon_level_prev = -1
    lcd.fill_rect(0, 16, WIDTH, BTN_Y - 16, BG)
    lt = time.localtime()
    pulse_time(lt, True)
    pulse_colon_level(6)
    pulse_bars(0.0, True)
    pulse_date(lt, True)


def pulse_update(lt, day_changed):
    pulse_time(lt)
    if anim_on:
        pulse_colon_level(6)
    else:
        pulse_colon_level(6 if colon_on else 0)
    pulse_bars(0.0)
    if day_changed:
        pulse_date(lt)


# ---- MODEL DAGITICI ----
def _dim(color, num, den):


    r = (color >> 11) & 0x1F
    g = (color >> 5) & 0x3F
    b = color & 0x1F
    br = (BG >> 11) & 0x1F
    bgc = (BG >> 5) & 0x3F
    bb = BG & 0x1F
    r = br + (r - br) * num // den
    g = bgc + (g - bgc) * num // den
    b = bb + (b - bb) * num // den
    return (r << 11) | (g << 5) | b


def draw_colon_level(level):

    global _digital_colon_level_prev
    if level == _digital_colon_level_prev:
        return
    _digital_colon_level_prev = level
    ty, _dw, dh, _dt, _dx, cx0, cw, _bx, _by, _bw, _bh, _dy1, _dy2 = _digital_layout()
    cx = cx0 + cw // 2
    lcd.fill_rect(cx - 7, ty, 15, dh, BG)
    if level > 0:
        col = _dim(FG, level, 6)
        lcd.circle(cx, ty + dh // 3, 6, col)
        lcd.circle(cx, ty + 2 * dh // 3, 6, col)


def draw_seconds_f(frac_total):

    global _seconds_fill_prev
    _ty, _dw, _dh, _dt, _dx, _cx, _cw, bx, by, bw, bh, _dy1, _dy2 = _digital_layout()
    fill = int(frac_total * bw)
    if fill < 0:
        fill = 0
    if fill > bw:
        fill = bw
    prev = _seconds_fill_prev
    if fill == prev:
        return
    if prev < 0 or fill < prev:
        lcd.fill_rect(bx, by, bw, bh, FG_DIM)
        if fill > 0:
            lcd.fill_rect(bx, by, fill, bh, FG)
    elif fill > prev:
        lcd.fill_rect(bx + prev, by, fill - prev, bh, FG)
    _seconds_fill_prev = fill


def big_colon_level(level):

    global _big_colon_level_prev
    if level == _big_colon_level_prev:
        return
    _big_colon_level_prev = level
    s = _big_prev if _big_prev else "00:00:00"
    adv = BIG_SIZE * 6
    startx = (WIDTH - len(s) * adv) // 2
    col = _dim(FG, level, 6) if level > 0 else BG
    for i in (2, 5):
        cx = startx + i * adv
        lcd.fill_rect(cx, BIG_Y, adv, BIG_SIZE * 7, BG)
        if level > 0:
            lcd.text(":", cx, BIG_Y, col, BIG_SIZE)


def _pulse_level(frac):

    t = frac * 2.0
    if t > 1.0:
        t = 2.0 - t
    lv = int(2 + t * 4)
    if lv < 0:
        lv = 0
    if lv > 6:
        lv = 6
    return lv


def face_static():
    if face_idx == 1:
        analog_static()
    elif face_idx == 2:
        big_static()
    elif face_idx == 3:
        pulse_static()
    else:
        digital_static()


def face_update(lt, day_changed):
    if face_idx == 1:
        analog_update(lt, day_changed)
    elif face_idx == 2:
        big_update(lt)
        if day_changed:
            big_date(lt)
    elif face_idx == 3:
        pulse_update(lt, day_changed)
    else:
        digital_update(lt, day_changed)


def face_anim(lt, frac):

    if face_idx == 1:

        return
    elif face_idx == 3:
        pulse_colon_level(_pulse_level(frac))
        pulse_bars(frac)
    elif face_idx == 2:
        big_colon_level(_pulse_level(frac))
    else:
        draw_colon_level(_pulse_level(frac))
        draw_seconds_f((lt[5] + frac) / 60.0)


def wipe_transition():

    if not anim_on:
        return
    step = 12
    for x in range(0, WIDTH, step):
        lcd.fill_rect(x, 16, step, BTN_Y - 16, BG)
        time.sleep_ms(3)


# ---- HAVA ANIMASYONU: KAR / YAGMUR ----

_weather_particles = []
_weather_seed = 12345
_weather_tick = 0


def _wrand(n):
    global _weather_seed
    if n <= 0:
        return 0
    _weather_seed = (_weather_seed * 1103515245 + 12345) & 0x7fffffff
    return _weather_seed % n


def _weather_kind(i):
    if weather_idx == 1:
        return 0
    return 1


def _weather_count():
    if face_idx != 2:
        return 0
    if weather_idx == 1:
        return 24
    return 18


def weather_interval_ms():
    if face_idx != 2:
        return 250
    if weather_idx == 2:
        return 75
    return 90


def _weather_spawn_x(kind):
    return _wrand(WIDTH)


def _weather_reset_particle(p, first=False):
    while len(p) < 8:
        p.append(0)
    kind = _weather_kind(_wrand(99))
    x = _weather_spawn_x(kind)
    y0 = 16
    y1 = BTN_Y - 8
    if first:
        y = y0 + _wrand(y1 - y0)
    else:
        y = y0 - _wrand(36)

    if kind == 0:
        spd = 1
        dx = 0
    else:
        spd = 3 + _wrand(3)
        dx = -1

    p[0] = x; p[1] = y
    p[2] = x; p[3] = y
    p[4] = spd
    p[5] = kind
    p[6] = _wrand(11)
    p[7] = dx


def weather_init():
    global _weather_particles, _weather_tick
    _weather_tick = 0
    _weather_particles = []
    if face_idx != 2:
        return
    for i in range(_weather_count()):
        p = [0, 0, 0, 0, 1, 0, 0, 0]
        _weather_reset_particle(p, True)
        _weather_particles.append(p)


def _weather_protected(px, py):
    if py < 16 or py >= BTN_Y - 3:
        return True
    if BIG_Y - 4 <= py <= BIG_Y + BIG_SIZE * 7 + 4:
        return True
    if 145 <= py <= 194:
        return True
    return False


def _weather_safe_rect(x, y, w, h):
    if x < 0 or y < 16 or x + w >= WIDTH or y + h >= BTN_Y - 2:
        return False
    if _weather_protected(x, y):
        return False
    if _weather_protected(x + w - 1, y):
        return False
    if _weather_protected(x, y + h - 1):
        return False
    if _weather_protected(x + w - 1, y + h - 1):
        return False
    if _weather_protected(x + w // 2, y + h // 2):
        return False
    return True


def _weather_erase(p):
    x = int(p[2]); y = int(p[3]); kind = p[5]
    if kind == 0:
        if _weather_safe_rect(x - 2, y - 2, 5, 5):
            lcd.fill_rect(x - 2, y - 2, 5, 5, BG)
    else:
        if _weather_safe_rect(x - 4, y, 9, 10):
            lcd.fill_rect(x - 4, y, 9, 10, BG)


def _weather_draw(p):
    x = int(p[0]); y = int(p[1]); kind = p[5]
    if kind == 0:
        if _weather_safe_rect(x - 2, y - 2, 5, 5):
            lcd.fill_rect(x, y - 1, 1, 3, FG)
            lcd.fill_rect(x - 1, y, 3, 1, FG)
    else:
        if _weather_safe_rect(x - 4, y, 9, 10):
            dx = p[7]
            if dx < 0:
                lcd.line(x, y, x - 3, y + 8, RAIN_COL)
            elif dx > 0:
                lcd.line(x, y, x + 3, y + 8, RAIN_COL)
            else:
                lcd.line(x, y, x, y + 8, RAIN_COL)


def weather_step():
    global _weather_tick
    if face_idx != 2:
        return
    if not _weather_particles or len(_weather_particles) != _weather_count():
        weather_init()
    _weather_tick += 1

    for p in _weather_particles:
        _weather_erase(p)

    for p in _weather_particles:
        p[2] = p[0]; p[3] = p[1]
        if p[5] == 0:
            p[1] += p[4]
            if (_weather_tick + p[6]) % 4 == 0:
                p[0] += _wrand(3) - 1
        else:
            p[0] += p[7]
            p[1] += p[4]
        if p[1] > BTN_Y - 8 or p[0] < 3 or p[0] > WIDTH - 4:
            _weather_reset_particle(p, False)
        _weather_draw(p)


def _forecast_value(daily, key, index):
    values = daily.get(key) or []
    return values[index] if index < len(values) else None


def _forecast_text(value):
    if isinstance(value, (bytes, bytearray)):
        try:
            return bytes(value).decode("utf-8")
        except Exception:
            try:
                return bytes(value).decode()
            except Exception:
                return ""
    try:
        return str(value)
    except Exception:
        return ""


def _forecast_date_label(value):
    try:
        parts = _forecast_text(value)[:10].split("-")
        day = int(parts[2])
        month = int(parts[1])
        return "%d %s" % (day, AYLAR[(month - 1) % 12])
    except Exception:
        return _forecast_text(value)[:10]


def _forecast_hm(value):
    text = _forecast_text(value)
    return text[11:16] if len(text) >= 16 else "--:--"


def weather_forecast_fetch():
    global _weather_cache_days, _weather_cache_ms
    global _weather_last_attempt, _weather_cache_version
    _weather_last_attempt = time.ticks_ms()
    if not is_online():
        return None, "HAVA ICIN WIFI GEREKLI"
    if USER_LAT is None or USER_LON is None:
        geo_locate()
    if USER_LAT is None or USER_LON is None:
        return None, "KONUM BULUNAMADI"
    path = ("/v1/forecast?latitude=%s&longitude=%s"
            "&current=temperature_2m"
            "&daily=temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,wind_speed_10m_max,"
            "wind_gusts_10m_max,sunrise,sunset"
            "&timezone=auto&forecast_days=16") % (
                _forecast_text(USER_LAT), _forecast_text(USER_LON))
    try:
        status, raw = https_get("api.open-meteo.com", path, 18)
        if status != 200 or not raw:
            return None, "HAVA SUNUCU KODU " + str(status)
        if isinstance(raw, (bytes, bytearray)):
            raw = _decode_buffer(raw)
        payload = json.loads(raw)
        daily = payload.get("daily") or {}
        current = (payload.get("current") or {}).get("temperature_2m")
        keys = ("time", "temperature_2m_max", "temperature_2m_min",
                "precipitation_probability_max", "wind_speed_10m_max",
                "wind_gusts_10m_max", "sunrise", "sunset")
        lengths = [len(daily.get(key) or []) for key in keys]
        count = min(lengths) if lengths else 0
        days = []
        for index in range(count):
            days.append({
                "date": _forecast_date_label(
                    _forecast_value(daily, "time", index)),
                "current": current if index == 0 else None,
                "low": _forecast_value(
                    daily, "temperature_2m_min", index),
                "high": _forecast_value(
                    daily, "temperature_2m_max", index),
                "rain": _forecast_value(
                    daily, "precipitation_probability_max", index),
                "wind": _forecast_value(
                    daily, "wind_speed_10m_max", index),
                "gust": _forecast_value(
                    daily, "wind_gusts_10m_max", index),
                "sunrise": _forecast_hm(
                    _forecast_value(daily, "sunrise", index)),
                "sunset": _forecast_hm(
                    _forecast_value(daily, "sunset", index)),
            })
        if not days:
            return None, "HAVA VERISI YOK"
        _weather_cache_days = days
        _weather_cache_ms = time.ticks_ms()
        _weather_cache_version += 1
        return days, None
    except Exception as exc:
        return None, "HAVA: " + str(exc)
    finally:
        gc.collect()


def _forecast_number(value, suffix=""):
    try:
        return str(int(float(value) + 0.5)) + suffix
    except Exception:
        return "-"


def _forecast_tile(x, y, w, h, title, first, second=""):
    lcd.fill_rect(x, y, w, h, DARKGRAY)
    lcd.rect(x, y, w, h, GRAY)
    lcd.text(title, x + (w - len(title) * 6) // 2, y + 8, TITLE_COL, 1)
    if second:
        lcd.text(first, x + (w - len(first) * 12) // 2, y + 28, FG, 2)
        lcd.text(second, x + (w - len(second) * 12) // 2, y + 57, FG, 2)
    else:
        lcd.text(first, x + (w - len(first) * 12) // 2, y + 43, FG, 2)


def _forecast_draw(days, index):
    day = days[index]
    lcd.fill(BG)
    date = day["date"]
    lcd.text(date, (WIDTH - len(date) * 12) // 2, 5, TITLE_COL, 2)
    temp_title = "SICAKLIK"
    if day.get("current") is not None:
        temp_title += " SIMDI " + _forecast_number(day["current"], " C")
    _forecast_tile(0, 28, 159, 87, temp_title,
                   "MAX " + _forecast_number(day["high"], " C"),
                   "MIN " + _forecast_number(day["low"], " C"))
    _forecast_tile(161, 28, 159, 87, "YAGMUR OLASILIGI",
                   "%" + _forecast_number(day["rain"]))
    _forecast_tile(0, 117, 159, 87, "RUZGAR / GUST",
                   _forecast_number(day["wind"], " km/h"),
                   "GUST " + _forecast_number(day["gust"], " km/h"))
    _forecast_tile(161, 117, 159, 87, "GUNES",
                   "DOGUS " + day["sunrise"],
                   "BATIS " + day["sunset"])
    buttons = (
        (0, 88, "GERI", BLUE, WHITE),
        (90, 114, "ONCEKI", DARKGRAY, WHITE),
        (206, 114, "SONRAKI", GREEN, BLACK),
    )
    for x, w, label, bg, fg in buttons:
        lcd.fill_rect(x, 208, w, 32, bg)
        lcd.rect(x, 208, w, 32, GRAY)
        lcd.text(label, x + (w - len(label) * 6) // 2, 220, fg, 1)


def run_weather_forecast():
    show_status_screen("HAVA ALINIYOR", TITLE_COL)
    days, err = weather_forecast_fetch()
    if err is not None:
        show_status_screen(to_screen_text(err)[:48], RED)
        time.sleep_ms(1800)
        return
    index = 0
    _forecast_draw(days, index)
    _wait_touch_release()
    while True:
        point = touch.read_fast()
        if point is None:
            time.sleep_ms(20)
            continue
        x, y = point
        if y < 208:
            continue
        _wait_touch_release()
        if x < 88:
            break
        if x < 205:
            if index > 0:
                index -= 1
        elif index + 1 < len(days):
            index += 1
        _forecast_draw(days, index)
    days = None
    gc.collect()

def draw_static():
    lcd.fill(BG)
    draw_status()
    face_static()
    draw_bottom()
    weather_init()


# ===================== ELLE SAAT/TARIH AYARI =====================
def _set_zone(x, y):
    if 206 <= y <= 234:
        if 20 <= x <= 150:
            return ("kaydet", 0, 0)
        if 170 <= x <= 300:
            return ("iptal", 0, 0)
    for i in range(5):
        ry = 38 + i * 32
        if ry <= y <= ry + 26:
            if 220 <= x <= 256:
                return ("f", i, -1)
            if 268 <= x <= 304:
                return ("f", i, 1)
    return None


def _set_draw_value(fields, i):


    f = fields[i]
    y = 38 + i * 32
    lcd.fill_rect(150, y, 64, 26, BG)
    val = str(f[1]) if f[0] == "YIL" else "%02d" % f[1]
    lcd.text(val, 156, y + 4, FG, 2)


def _set_draw(fields):
    lcd.fill(BG)
    title = "SAAT AYARI"
    lcd.text(title, (WIDTH - len(title) * 12) // 2, 6, FG, 2)
    for i in range(5):
        f = fields[i]
        y = 38 + i * 32
        lcd.text(f[0], 10, y + 4, FG, 2)
        _set_draw_value(fields, i)
        lcd.rect(220, y, 36, 26, GRAY)
        lcd.text("-", 234, y + 6, FG, 2)
        lcd.rect(268, y, 36, 26, GRAY)
        lcd.text("+", 282, y + 6, FG, 2)
    lcd.rect(20, 206, 130, 28, GREEN)
    lcd.text("KAYDET", 20 + (130 - 6 * 6) // 2, 215, GREEN, 1)
    lcd.rect(170, 206, 130, 28, RED)
    lcd.text("IPTAL", 170 + (130 - 5 * 6) // 2, 215, RED, 1)


def run_set():
    lt = time.localtime()
    fields = [
        ["SAAT", lt[3], 0, 23],
        ["DAKIKA", lt[4], 0, 59],
        ["GUN", lt[2], 1, 31],
        ["AY", lt[1], 1, 12],
        ["YIL", lt[0], 2024, 2099],
    ]
    _set_draw(fields)
    need_release = True
    while True:
        p = touch.read_screen()
        if p is None:
            need_release = False
            time.sleep_ms(30)
            continue
        if need_release:
            time.sleep_ms(30)
            continue
        need_release = True
        z = _set_zone(p[2], p[3])
        if z is None:
            continue
        kind, idx, delta = z
        if kind == "iptal":
            return
        if kind == "kaydet":
            if rtc is not None:
                try:
                    rtc.datetime((fields[4][1], fields[3][1], fields[2][1], 0,
                                  fields[0][1], fields[1][1], 0, 0))
                except Exception:
                    pass
            return
        f = fields[idx]
        v = f[1] + delta
        if v < f[2]:
            v = f[3]
        if v > f[3]:
            v = f[2]
        f[1] = v
        _set_draw_value(fields, idx)


# ===================== HIZLI AYAR PANELI =====================
CFG_FILE = "saat_cfg.txt"


def save_cfg():
    data = "%d %d %d %d %d %d %d %d %d %d %d %d %d %d\n" % (
        mode_idx, face_idx, bright_idx,
        1 if screen_flip else 0,
        1 if USE_24H else 0,
        ans_size_idx, ans_len_idx,
        weather_idx, prayer_mode_idx,
        prayer_size_idx,
        prayer_thick_idx,
        prayer_gap_idx,
        bright_value,
        2)
    safe_write_text(CFG_FILE, data)


def load_cfg():
    global mode_idx, face_idx, bright_idx, screen_flip, USE_24H
    global bright_value
    global ans_size_idx, ans_len_idx, weather_idx, prayer_mode_idx
    global prayer_size_idx, prayer_thick_idx, prayer_gap_idx
    try:
        f = open(CFG_FILE)
        d = f.read()
        f.close()
        p = d.split()
        if len(p) >= 5:
            mode_idx = 0
            face_idx = int(p[1]) % FACE_COUNT
            bright_idx = int(p[2]) % len(BRIGHT_LEVELS)
            screen_flip = (p[3] == "1")
            USE_24H = True
        if len(p) >= 7:
            ans_size_idx = int(p[5]) % len(SIZE_PROFILES)
            ans_len_idx = int(p[6]) % len(LEN_PROFILES)
        if len(p) >= 8:
            v = int(p[7])
            weather_idx = 1 if v == 1 else 2
        if len(p) >= 9:
            prayer_mode_idx = int(p[8]) % len(PRAYER_MODE_NAMES)
        if len(p) >= 10:
            saved_prayer_size = int(p[9])
            if len(p) >= 14 and p[13] == "2":
                prayer_size_idx = saved_prayer_size % len(PRAYER_SIZE_NAMES)
            else:
                prayer_size_idx = min(saved_prayer_size + 1,
                                      len(PRAYER_SIZE_NAMES) - 1)
        prayer_thick_idx = 0
        if len(p) >= 12:
            prayer_gap_idx = int(p[11]) % len(PRAYER_GAP_NAMES)
        bright_value = BRIGHT_LEVELS[bright_idx]
        if len(p) >= 13:
            saved_brightness = int(p[12])
            if BRIGHT_MIN <= saved_brightness <= 65535:
                nearest = 0
                nearest_diff = abs(BRIGHT_LEVELS[0] - saved_brightness)
                for i in range(1, len(BRIGHT_LEVELS)):
                    diff = abs(BRIGHT_LEVELS[i] - saved_brightness)
                    if diff < nearest_diff:
                        nearest = i
                        nearest_diff = diff
                bright_idx = nearest
                bright_value = BRIGHT_LEVELS[bright_idx]
    except Exception:
        pass
    mode_idx = 0
    prayer_thick_idx = 0
    USE_24H = True
    apply_mode()


# ---- kucuk yardimcilar ----
def _wait_touch_release():
    while touch.read_fast() is not None:
        time.sleep_ms(10)


# ---- TEK EKRANDA TUM AYARLAR ----
_SET_BACK_Y = 214
_SET_COL_W = WIDTH // 4
_BRIGHT_SLIDER_TOP = 58
_BRIGHT_SLIDER_BOTTOM = 178


def _settings_col_text(col, text, y, color, size=1):
    width = len(text) * 6 * size
    x = col * _SET_COL_W + (_SET_COL_W - width) // 2
    lcd.text(text, x, y, color, size)


def _settings_col_scaled_text(col, text, y, color, style):
    width = _scaled_text_width(text, style)
    x = col * _SET_COL_W + (_SET_COL_W - width) // 2
    _draw_scaled_text(text, x, y, color, style)


def _settings_clear_col(col):
    x = col * _SET_COL_W
    lcd.fill_rect(x + 1, 39, _SET_COL_W - 1, _SET_BACK_Y - 39, BG)


def _settings_draw_sor(clear=True):
    if clear:
        _settings_clear_col(0)
    lcd.hline(0, 123, _SET_COL_W, DARKGRAY)
    _settings_col_text(0, "YAZI", 58, GRAY)
    _settings_col_text(0, SIZE_NAMES[ans_size_idx], 82, FG)
    _settings_col_text(0, "CEVAP", 143, GRAY)
    _settings_col_text(0, LEN_PROFILES[ans_len_idx][0], 167, FG)


def _settings_draw_prayer(clear=True):
    if clear:
        _settings_clear_col(1)
    _settings_col_text(1, "MOD", 59, GRAY)
    _settings_col_text(1, PRAYER_MODE_NAMES[prayer_mode_idx], 82, FG)
    lcd.hline(_SET_COL_W, 123, _SET_COL_W, DARKGRAY)
    _settings_col_text(1, "BOYUT", 143, GRAY)
    name = PRAYER_SIZE_NAMES[prayer_size_idx]
    style = PRAYER_SIZE_STYLES[prayer_size_idx]
    _settings_col_scaled_text(1, name, 166, FG, style)


def _brightness_slider_y(value=None):
    if value is None:
        value = bright_value
    best = 0
    best_diff = abs(BRIGHT_LEVELS[0] - value)
    for i in range(1, len(BRIGHT_LEVELS)):
        diff = abs(BRIGHT_LEVELS[i] - value)
        if diff < best_diff:
            best = i
            best_diff = diff
    return (_BRIGHT_SLIDER_TOP +
            best * (_BRIGHT_SLIDER_BOTTOM - _BRIGHT_SLIDER_TOP) //
            (len(BRIGHT_LEVELS) - 1))


def _brightness_from_y(y):
    if y < _BRIGHT_SLIDER_TOP:
        y = _BRIGHT_SLIDER_TOP
    if y > _BRIGHT_SLIDER_BOTTOM:
        y = _BRIGHT_SLIDER_BOTTOM
    span_y = _BRIGHT_SLIDER_BOTTOM - _BRIGHT_SLIDER_TOP
    idx = ((y - _BRIGHT_SLIDER_TOP) * (len(BRIGHT_LEVELS) - 1) +
           span_y // 2) // span_y
    return BRIGHT_LEVELS[idx]


def _settings_draw_brightness(clear=True, old_y=None):
    bx = 2 * _SET_COL_W + 62
    if clear:
        _settings_clear_col(2)
    elif old_y is not None:
        lcd.fill_rect(bx - 12, old_y - 7, 25, 15, BG)
    lcd.vline(bx, _BRIGHT_SLIDER_TOP,
              _BRIGHT_SLIDER_BOTTOM - _BRIGHT_SLIDER_TOP + 1, GRAY)
    for i, label in enumerate(BRIGHT_NAMES):
        y = (_BRIGHT_SLIDER_TOP +
             i * (_BRIGHT_SLIDER_BOTTOM - _BRIGHT_SLIDER_TOP) //
             (len(BRIGHT_NAMES) - 1))
        lcd.text(label, 2 * _SET_COL_W + 5, y - 3, FG, 1)
        lcd.hline(bx - 6, y, 13, GRAY)
    thumb_y = _brightness_slider_y()
    lcd.fill_rect(bx - 10, thumb_y - 5, 21, 11, TITLE_COL)
    lcd.rect(bx - 10, thumb_y - 5, 21, 11, FG)


def _settings_draw_direction(preview_flip, clear=True):
    if clear:
        _settings_clear_col(3)
    direction = "TERS" if preview_flip else "NORMAL"
    ex = 3 * _SET_COL_W + _SET_COL_W // 2
    device_x = ex - 29
    device_y = 60 if preview_flip else 47
    device_w = 59
    device_h = 40
    port_x = ex + 12 if preview_flip else ex - 12
    lcd.rect(device_x, device_y, device_w, device_h, FG)
    lcd.rect(device_x + 4, device_y + 4, device_w - 8, device_h - 8, GRAY)
    if preview_flip:

        lcd.fill_rect(port_x - 5, device_y - 3, 11, 4, TITLE_COL)
        lcd.fill_rect(port_x - 8, device_y - 13, 17, 11, DARKGRAY)
        lcd.rect(port_x - 8, device_y - 13, 17, 11, FG)
        lcd.fill_rect(3 * _SET_COL_W + 1, device_y - 10,
                      port_x - 8 - (3 * _SET_COL_W + 1), 5, GRAY)
        lcd.hline(3 * _SET_COL_W + 1, device_y - 11,
                  port_x - 8 - (3 * _SET_COL_W + 1), FG)
    else:

        port_y = device_y + device_h - 1
        lcd.fill_rect(port_x - 5, port_y, 11, 4, TITLE_COL)
        lcd.fill_rect(port_x - 8, port_y + 3, 17, 11, DARKGRAY)
        lcd.rect(port_x - 8, port_y + 3, 17, 11, FG)
        lcd.fill_rect(port_x + 9, port_y + 6,
                      3 * _SET_COL_W + _SET_COL_W - (port_x + 9), 5, GRAY)
        lcd.hline(port_x + 9, port_y + 5,
                  3 * _SET_COL_W + _SET_COL_W - (port_x + 9), FG)
    actions = (
        (112, "YON " + direction),
    )
    x = 3 * _SET_COL_W + 6
    w = _SET_COL_W - 12
    for y, label in actions:
        lcd.fill_rect(x, y, w, 27, DARKGRAY)
        lcd.rect(x, y, w, 27, GRAY)
        lcd.text(label, x + (w - len(label) * 6) // 2, y + 10, WHITE, 1)


def _settings_draw(preview_flip):
    lcd.fill(BG)
    for col in range(4):
        x = col * _SET_COL_W
        lcd.fill_rect(x, 0, _SET_COL_W, 38, DARKGRAY)
        if col:
            lcd.vline(x, 0, _SET_BACK_Y, GRAY)
    _settings_col_text(0, "SOR", 14, WHITE)
    _settings_col_text(1, "NAMAZ", 14, WHITE)
    _settings_col_text(2, "PARLAKLIK", 14, WHITE)
    _settings_col_text(3, "EKRAN YONU", 14, WHITE)
    lcd.hline(0, 38, WIDTH, GRAY)
    _settings_draw_sor(False)
    _settings_draw_prayer(False)
    _settings_draw_brightness(False)
    _settings_draw_direction(preview_flip, False)
    lcd.fill_rect(0, _SET_BACK_Y, WIDTH, HEIGHT - _SET_BACK_Y, DARKGRAY)
    lcd.hline(0, _SET_BACK_Y, WIDTH, GRAY)
    lcd.text("GERI", (WIDTH - 24) // 2, 224, WHITE, 1)


def _settings_change(col, y):
    global prayer_mode_idx, prayer_size_idx, prayer_gap_idx
    global ans_size_idx, ans_len_idx

    if col == 0:
        if y < 123:
            ans_size_idx = (ans_size_idx + 1) % len(SIZE_PROFILES)
        else:
            ans_len_idx = (ans_len_idx + 1) % len(LEN_PROFILES)
    elif col == 1:
        if y < 123:
            prayer_mode_idx = (prayer_mode_idx + 1) % len(PRAYER_MODE_NAMES)
        else:
            prayer_size_idx = (prayer_size_idx + 1) % len(PRAYER_SIZE_NAMES)
    else:
        return False
    save_cfg()
    return True


def _settings_set_brightness(y):
    global bright_value, bright_idx
    old_y = _brightness_slider_y()
    value = _brightness_from_y(y)
    if value == bright_value:
        return
    bright_value = value
    nearest = 0
    nearest_diff = abs(BRIGHT_LEVELS[0] - bright_value)
    for i in range(1, len(BRIGHT_LEVELS)):
        diff = abs(BRIGHT_LEVELS[i] - bright_value)
        if diff < nearest_diff:
            nearest = i
            nearest_diff = diff
    bright_idx = nearest
    if bl_pwm is not None:
        bl_pwm.duty_u16(bright_value)
    _settings_draw_brightness(False, old_y)


def _settings_header_held(col):
    """Ayni ayar basliginda uzun basma yapildiysa True dondurur."""
    started = time.ticks_ms()
    while True:
        p = touch.read_fast()
        if p is None:
            return False
        x, y = p
        if y >= 38 or min(3, x // _SET_COL_W) != col:
            return False
        if time.ticks_diff(time.ticks_ms(), started) >= LONG_PRESS_MS:
            _wait_touch_release()
            return True
        time.sleep_ms(20)




def run_all_settings():
    global screen_flip
    dragging_brightness = False
    _settings_draw(screen_flip)
    _wait_touch_release()
    last_touch = 0
    while True:
        p = touch.read_fast()
        if p is None:
            if dragging_brightness:
                dragging_brightness = False
                save_cfg()
            time.sleep_ms(15)
            continue
        x, y = p
        if dragging_brightness:
            _settings_set_brightness(y)
            time.sleep_ms(12)
            continue
        now = time.ticks_ms()
        if time.ticks_diff(now, last_touch) < TOUCH_DEBOUNCE_MS:
            time.sleep_ms(10)
            continue
        last_touch = now
        if y >= _SET_BACK_Y:
            _wait_touch_release()
            return
        col = min(3, x // _SET_COL_W)
        if y < 38:
            if _settings_header_held(col):
                if col == 3:
                    run_general_test()
                    _settings_draw(screen_flip)
                elif col == 0:
                    run_connection_diagnostics()
                    _settings_draw(screen_flip)
            continue
        if col == 2:
            dragging_brightness = True
            _settings_set_brightness(y)
            continue
        _wait_touch_release()
        if col == 3:
            if y < _SET_BACK_Y:
                screen_flip = not screen_flip
                lcd.set_rotation(screen_flip)
                save_cfg()
                _settings_draw(screen_flip)
        elif _settings_change(col, y):
            if col == 0:
                _settings_draw_sor()
            else:
                _settings_draw_prayer()


def _fast_disc(cx, cy, r, color):
    rr = r * r
    for yy in range(-r, r + 1):
        xx = r
        y2 = yy * yy
        while xx > 0 and xx * xx + y2 > rr:
            xx -= 1
        lcd.fill_rect(cx - xx, cy + yy, xx * 2 + 1, 1, color)


def _draw_round_rect(x, y, w, h, r, fill_col, border_col=None):


    if r <= 0:
        lcd.fill_rect(x, y, w, h, fill_col)
        if border_col is not None:
            lcd.rect(x, y, w, h, border_col)
        return
    if r * 2 > h:
        r = h // 2
    if r * 2 > w:
        r = w // 2
    lcd.fill_rect(x + r, y, w - 2 * r, h, fill_col)
    lcd.fill_rect(x, y + r, r, h - 2 * r, fill_col)
    lcd.fill_rect(x + w - r, y + r, r, h - 2 * r, fill_col)
    rr = r * r
    for dy in range(r):
        yy = r - 1 - dy
        dx = int(math.sqrt(rr - yy * yy)) if rr > yy * yy else 0
        if dx <= 0:
            continue
        lcd.fill_rect(x + r - dx, y + dy, dx, 1, fill_col)
        lcd.fill_rect(x + w - r, y + dy, dx, 1, fill_col)
        lcd.fill_rect(x + r - dx, y + h - 1 - dy, dx, 1, fill_col)
        lcd.fill_rect(x + w - r, y + h - 1 - dy, dx, 1, fill_col)
    if border_col is None:
        return
    lcd.hline(x + r, y, w - 2 * r, border_col)
    lcd.hline(x + r, y + h - 1, w - 2 * r, border_col)
    lcd.vline(x, y + r, h - 2 * r, border_col)
    lcd.vline(x + w - 1, y + r, h - 2 * r, border_col)
    for dy in range(r):
        yy = r - 1 - dy
        dx = int(math.sqrt(rr - yy * yy)) if rr > yy * yy else 0
        if dx <= 0:
            continue
        cx0 = x + r - dx
        cx1 = x + w - r + dx - 1
        lcd.fill_rect(cx0, y + dy, 1, 1, border_col)
        lcd.fill_rect(cx1, y + dy, 1, 1, border_col)
        lcd.fill_rect(cx0, y + h - 1 - dy, 1, 1, border_col)
        lcd.fill_rect(cx1, y + h - 1 - dy, 1, 1, border_col)


def _draw_round_button(x, y, w, h, border_col, fill_col, label, fg, r=8):
    _draw_round_rect(x, y, w, h, r, fill_col, border_col)
    if label:
        tx = x + (w - len(label) * 6) // 2
        ty = y + (h - 7) // 2
        lcd.text(label, tx, ty, fg, 1)


def _fast_button_base(cx, cy, r, active):


    bg = FG if active else DARKGRAY
    fg = BG if active else WHITE
    _fast_disc(cx, cy, r, bg)
    lcd.ring(cx, cy, r, GRAY)
    lcd.ring(cx, cy, r - 1, GRAY)
    return fg


def _draw_circle_button(cx, cy, r, label, active=False, sub=""):
    fg = _fast_button_base(cx, cy, r, active)
    if label:
        size = 2 if len(label) <= 2 else 1
        adv = 12 if size == 2 else 6
        lcd.text(label, cx - (len(label) * adv) // 2, cy - (7 * size) // 2, fg, size)
    if sub:
        lcd.text(sub, cx - (len(sub) * 6) // 2, cy + r + 4, GRAY, 1)


def _draw_rotate_icon(cx, cy, active):
    fg = _fast_button_base(cx, cy, 24, active)
    lcd.rect(cx - 13, cy - 7, 19, 13, fg)
    lcd.fill_rect(cx - 5, cy + 8, 4, 2, fg)
    lcd.hline(cx - 10, cy + 11, 14, fg)
    lcd.line(cx + 9, cy - 11, cx + 15, cy - 6, fg)
    lcd.line(cx + 15, cy - 6, cx + 12, cy, fg)
    lcd.line(cx + 15, cy - 6, cx + 18, cy - 12, fg)
    lcd.text("DON", cx - 9, cy + 29, GRAY, 1)


def _panel_header(title):
    lcd.fill(BG)
    lcd.text(title, (WIDTH - len(title) * 12) // 2, 8, TITLE_COL, 2)
    lcd.hline(0, 34, WIDTH, DARKGRAY)


# ---- SOR ayari: ayri menu + kaydirgaclar ----
def _sor_menu_draw():
    _panel_header("GPT AYARI")
    items = [
        ("YAZI BOYUTU", SIZE_NAMES[ans_size_idx]),
        ("CEVAP UZUNLUK", LEN_PROFILES[ans_len_idx][0]),
        ("GERI", ""),
    ]
    for i in range(3):
        y = 58 + i * 46
        lbl, val = items[i]
        col = GREEN if i == 2 else WHITE
        lcd.fill_rect(16, y, WIDTH - 32, 34, DARKGRAY)
        lcd.rect(16, y, WIDTH - 32, 34, GRAY)
        lcd.text(lbl, 28, y + 10, col, 1)
        if val:
            lcd.text(val, WIDTH - 28 - len(val) * 6, y + 10, WHITE, 1)
    lcd.text("Secmek icin dokun", 100, 206, GRAY, 1)


def _sor_menu_hit(x, y):
    for i in range(3):
        yy = 58 + i * 46
        if 16 <= x <= WIDTH - 16 and yy <= y <= yy + 34:
            return i
    return None


def _slider_value_from_x(x, count):
    x0 = 42
    x1 = WIDTH - 42
    if x < x0:
        x = x0
    if x > x1:
        x = x1
    if count <= 1:
        return 0
    return int((x - x0) * (count - 1) // (x1 - x0))


def _slider_knob_x(value, count):
    x0 = 42
    x1 = WIDTH - 42
    if count <= 1:
        return x0
    return x0 + (x1 - x0) * value // (count - 1)


def _draw_slider_screen(title, value, count, preview, hint, preview_size=2):
    _panel_header(title)
    lcd.text(hint, (WIDTH - len(hint) * 6) // 2, 198, GRAY, 1)
    lcd.fill_rect(0, 50, WIDTH, 60, BG)
    size = preview_size
    adv = 6 * size
    px = (WIDTH - len(preview) * adv) // 2
    if px < 4:
        px = 4
    lcd.text(preview, px, 70, FG, size)
    y = 142
    lcd.hline(42, y, WIDTH - 84, GRAY)
    lcd.hline(42, y + 1, WIDTH - 84, GRAY)
    kx = _slider_knob_x(value, count)
    lcd.fill_rect(kx - 8, y - 11, 16, 24, FG)
    lcd.rect(kx - 8, y - 11, 16, 24, GRAY)
    lcd.fill_rect(0, 214, WIDTH, 26, DARKGRAY)
    lcd.hline(0, 214, WIDTH, GRAY)
    lcd.text("GERI", (WIDTH - 24) // 2, 224, WHITE, 1)


def _run_slider(title, start_value, count, preview_func, hint):
    value = start_value
    dragging = False
    last_value = -1
    while True:
        if value != last_value:
            prev, psize = preview_func(value)
            _draw_slider_screen(title, value, count, prev, hint, psize)
            last_value = value
        p = touch.read_fast()
        if p is None:
            dragging = False
            time.sleep_ms(20)
            continue
        x, y = p
        if y >= 214:
            _wait_touch_release()
            return value
        if 118 <= y <= 168 or dragging:
            dragging = True
            value = _slider_value_from_x(x, count)
        time.sleep_ms(20)


def run_sor_settings():
    global ans_size_idx, ans_len_idx
    _sor_menu_draw()
    _wait_touch_release()
    last = 0
    while True:
        p = touch.read_fast()
        if p is None:
            time.sleep_ms(20)
            continue
        now = time.ticks_ms()
        if time.ticks_diff(now, last) < TOUCH_DEBOUNCE_MS:
            continue
        last = now
        x, y = p
        sel = _sor_menu_hit(x, y)
        if sel is None:
            continue
        _wait_touch_release()
        if sel == 0:
            def pv(v):
                return ("ORNEK CEVAP", 1 + v)
            ans_size_idx = _run_slider("YAZI BOYUTU", ans_size_idx,
                                       len(SIZE_PROFILES), pv,
                                       "Yaziyi buyutmek icin imleci kaydir")
            save_cfg()
            _sor_menu_draw()
        elif sel == 1:
            def pv2(v):
                return (LEN_PROFILES[v][0], 2)
            ans_len_idx = _run_slider("CEVAP UZUNLUGU", ans_len_idx,
                                      len(LEN_PROFILES), pv2,
                                      "Cevap uzunlugu icin imleci kaydir")
            save_cfg()
            _sor_menu_draw()
        elif sel == 2:
            return


# ---- NAMAZ AYARI: ayri menu ----
_PRAYER_MODE_Y0 = 38
_PRAYER_MODE_H = 25
_PRAYER_MODE_GAP = 30
_PRAYER_SIZE_Y = 138
_PRAYER_GAP_Y = 178


def _draw_prayer_mode_row(i):
    name = PRAYER_MODE_NAMES[i]
    y = _PRAYER_MODE_Y0 + i * _PRAYER_MODE_GAP
    active = (i == prayer_mode_idx)
    lcd.fill_rect(22, y, WIDTH - 44, _PRAYER_MODE_H, FG if active else DARKGRAY)
    lcd.rect(22, y, WIDTH - 44, _PRAYER_MODE_H, GRAY)
    lcd.text(name, 42, y + 7, BG if active else WHITE, 1)
    if active:
        lcd.text("SECILI", WIDTH - 82, y + 7, BG, 1)


def _draw_prayer_option_row(y, label, value, enabled=True):
    bg = DARKGRAY if enabled else BG
    fg = WHITE if enabled else DARKGRAY
    val_col = WHITE if enabled else DARKGRAY
    lcd.fill_rect(22, y, WIDTH - 44, 24, bg)
    lcd.rect(22, y, WIDTH - 44, 24, GRAY if enabled else DARKGRAY)
    lcd.text(label, 42, y + 7, fg, 1)
    lcd.text(value, WIDTH - 44 - len(value) * 6, y + 7, val_col, 1)


def _draw_prayer_action_rows():
    _draw_prayer_option_row(_PRAYER_SIZE_Y, "BUYUKLUK", PRAYER_SIZE_NAMES[prayer_size_idx], True)
    if prayer_mode_idx == 2:
        _draw_prayer_option_row(_PRAYER_GAP_Y, "BOSLUK", PRAYER_GAP_NAMES[prayer_gap_idx], True)
    else:
        _draw_prayer_option_row(_PRAYER_GAP_Y, "BOSLUK", "HEPSI ICIN", False)


def _prayer_menu_draw():
    _panel_header("NAMAZ AYARI")
    for i in range(len(PRAYER_MODE_NAMES)):
        _draw_prayer_mode_row(i)
    _draw_prayer_action_rows()
    lcd.fill_rect(0, 216, WIDTH, 24, DARKGRAY)
    lcd.hline(0, 216, WIDTH, GRAY)
    lcd.text("GERI", (WIDTH - 24) // 2, 225, WHITE, 1)


def _prayer_menu_hit(x, y):
    for i in range(len(PRAYER_MODE_NAMES)):
        yy = _PRAYER_MODE_Y0 + i * _PRAYER_MODE_GAP
        if 22 <= x <= WIDTH - 22 and yy <= y <= yy + _PRAYER_MODE_H:
            return i
    if 22 <= x <= WIDTH - 22 and _PRAYER_SIZE_Y <= y <= _PRAYER_SIZE_Y + 24:
        return 3
    if 22 <= x <= WIDTH - 22 and _PRAYER_GAP_Y <= y <= _PRAYER_GAP_Y + 24:
        return 4
    if y >= 216:
        return 5
    return None


def _draw_prayer_slider_screen(title, value, count, mode):
    _panel_header(title)
    lcd.fill_rect(0, 48, WIDTH, 72, BG)
    col = FG
    if mode == "size":
        txt = PRAYER_SIZE_NAMES[value]
        style = PRAYER_SIZE_STYLES[value]
        x = (WIDTH - _scaled_text_width(txt, style)) // 2
        y = 82 - style[1] // 2
        _draw_scaled_text(txt, x, y, col, style)
        hint = "Namaz yazisi boyutu icin kaydir"
    else:
        gap = " " * (value + 1)
        txt = "IM 05:20" + gap + "OG 13:10" + gap + "IK 16:45" + gap + "AK 20:20"
        style = _prayer_text_style(txt, WIDTH - 4)
        x = (WIDTH - _scaled_text_width(txt, style)) // 2
        _draw_scaled_text(txt, x, 78, col, style)
        hint = "HEPSI modunda bosluk icin kaydir"
    lcd.text(hint, (WIDTH - len(hint) * 6) // 2, 198, GRAY, 1)

    y = 142
    lcd.hline(42, y, WIDTH - 84, GRAY)
    lcd.hline(42, y + 1, WIDTH - 84, GRAY)
    kx = _slider_knob_x(value, count)
    lcd.fill_rect(kx - 8, y - 11, 16, 24, FG)
    lcd.rect(kx - 8, y - 11, 16, 24, GRAY)
    lcd.fill_rect(0, 216, WIDTH, 24, DARKGRAY)
    lcd.hline(0, 216, WIDTH, GRAY)
    lcd.text("GERI", (WIDTH - 24) // 2, 225, WHITE, 1)


def _run_prayer_slider(title, start_value, count, mode):
    value = start_value
    last_value = -1
    dragging = False
    while True:
        if value != last_value:
            _draw_prayer_slider_screen(title, value, count, mode)
            last_value = value
        p = touch.read_fast()
        if p is None:
            dragging = False
            time.sleep_ms(20)
            continue
        x, y = p
        if y >= 216:
            _wait_touch_release()
            return value
        if 118 <= y <= 168 or dragging:
            dragging = True
            value = _slider_value_from_x(x, count)
        time.sleep_ms(20)


def run_prayer_settings():
    global prayer_mode_idx, prayer_size_idx, prayer_gap_idx
    if prayer_mode_idx != 0:
        prayer_sync()
    _prayer_menu_draw()
    _wait_touch_release()
    last = 0
    while True:
        p = touch.read_fast()
        if p is None:
            time.sleep_ms(20)
            continue
        now = time.ticks_ms()
        if time.ticks_diff(now, last) < TOUCH_DEBOUNCE_MS:
            continue
        last = now
        x, y = p
        sel = _prayer_menu_hit(x, y)
        if sel is None:
            continue
        _wait_touch_release()
        if sel == 5:
            return
        if 0 <= sel <= 2:
            if sel != prayer_mode_idx:
                old = prayer_mode_idx
                prayer_mode_idx = sel
                if prayer_mode_idx != 0:
                    prayer_sync()
                save_cfg()
                _draw_prayer_mode_row(old)
                _draw_prayer_mode_row(prayer_mode_idx)
                _draw_prayer_action_rows()
        elif sel == 3:
            prayer_size_idx = _run_prayer_slider("YAZI BUYUKLUGU", prayer_size_idx,
                                                 len(PRAYER_SIZE_NAMES), "size")
            save_cfg()
            _prayer_menu_draw()
        elif sel == 4 and prayer_mode_idx == 2:
            prayer_gap_idx = _run_prayer_slider("BOSLUK", prayer_gap_idx,
                                                len(PRAYER_GAP_NAMES), "gap")
            save_cfg()
            _prayer_menu_draw()


# ---- BAGLANTI / DEPOLAMA TESHISI ----
def _storage_kb():
    try:
        info = os.statvfs("/")
        block = int(info[0])
        return (int(info[2]) * block // 1024,
                int(info[3]) * block // 1024)
    except Exception:
        return 0, 0


def _cache_file_count():
    count = 0
    try:
        for name in os.listdir():
            if name.startswith(LIVE_CACHE_PREFIX) and name.endswith(".txt"):
                count += 1
    except Exception:
        pass
    return count


def _diagnostic_values():
    gc.collect()
    online = is_online()
    ip = "-"
    rssi = None
    if online:
        try:
            station = wlan if wlan is not None else network.WLAN(network.STA_IF)
            ip = station.ifconfig()[0]
            try:
                rssi = station.status("rssi")
            except Exception:
                rssi = None
        except Exception:
            pass
    dns_ok = False
    if online:
        try:
            socket.getaddrinfo("api.openai.com", 443)
            dns_ok = True
        except Exception:
            pass
    https_ok = False
    if dns_ok:
        try:
            status, _text = https_get("api.openai.com", "/v1/models", 12)
            https_ok = status in (200, 401, 403)
            _text = None
        except Exception:
            pass
    total_kb, free_kb = _storage_kb()
    try:
        ram_kb = gc.mem_free() // 1024
    except Exception:
        ram_kb = 0
    return (
        ("WIFI", "OK" if online else "YOK", GREEN if online else RED),
        ("IP", ip, FG),
        ("SINYAL", (str(rssi) + " dBm") if rssi is not None else "-", FG),
        ("DNS", "OK" if dns_ok else "HATA", GREEN if dns_ok else RED),
        ("HTTPS", "OK" if https_ok else "HATA", GREEN if https_ok else RED),
        ("NTP", "OK" if ntp_ok else "BEKLIYOR", GREEN if ntp_ok else AMBER),
        ("API ANAHTARI", "HAZIR" if OPENAI_API_KEY.strip() else "YOK",
         GREEN if OPENAI_API_KEY.strip() else RED),
        ("BOS RAM", str(ram_kb) + " KB", FG),
        ("BOS DEPO", str(free_kb) + "/" + str(total_kb) + " KB", FG),
        ("ONBELLEK", str(_cache_file_count()) + "/" +
         str(LIVE_CACHE_LIMIT), FG),
    )


def _diagnostic_draw(rows=None):
    lcd.fill(BG)
    lcd.text("BAGLANTI TESHISI", 64, 8, TITLE_COL, 2)
    lcd.hline(0, 32, WIDTH, DARKGRAY)
    if rows is None:
        lcd.text("TEST EDILIYOR", 118, 108, AMBER, 1)
    else:
        y = 39
        for label, value, color in rows:
            lcd.text(label, 8, y, GRAY, 1)
            width = len(value) * 6
            lcd.text(value, WIDTH - width - 8, y, color, 1)
            y += 16
        lcd.text("SURUM " + APP_VERSION, 8, 199, GRAY, 1)
    lcd.fill_rect(0, 214, 158, 26, DARKGRAY)
    lcd.fill_rect(162, 214, 158, 26, DARKGRAY)
    lcd.vline(160, 214, 26, GRAY)
    lcd.text("YENILE", 61, 223, WHITE, 1)
    lcd.text("GERI", 230, 223, WHITE, 1)


def run_connection_diagnostics():
    _wait_touch_release()
    while True:
        _diagnostic_draw()
        rows = _diagnostic_values()
        _diagnostic_draw(rows)
        _wait_touch_release()
        while True:
            p = touch.read_fast()
            if p is None:
                time.sleep_ms(20)
                continue
            x, y = p
            if y >= 210:
                _wait_touch_release()
                if x >= WIDTH // 2:
                    return
                break


# ---- GENEL SISTEM TESTI ----
_GENERAL_TEST_ROWS = (
    "CALISMA SURESI", "CPU SICAKLIK", "BASLAMA NEDENI", "WIFI SINYALI",
    "IP", "OTA SURUMU", "SON HATA", "VOLTAJ", "CPU", "RAM",
    "GPT MODELI", "DOSYALAR", "EKRAN YENILEME", "OPENAI YANIT",
)

_GENERAL_TEST_ROW_Y = 36
_GENERAL_TEST_ROW_STEP = 12


def _cpu_temperature_c():
    """Pico/Pico 2 dahili sensorunden yaklasik yonga sicakligini oku."""
    try:
        channel = ADC.CORE_TEMP if hasattr(ADC, "CORE_TEMP") else 4
        sensor = ADC(channel)
        total = 0
        for _ in range(8):
            total += sensor.read_u16()
        voltage = (total / 8) * 3.3 / 65535
        return 27 - (voltage - 0.706) / 0.001721
    except Exception:
        return None


def _uptime_text():
    seconds = time.ticks_ms() // 1000
    days = seconds // 86400
    hours = (seconds // 3600) % 24
    minutes = (seconds // 60) % 60
    seconds %= 60
    if days:
        return "%dg %02d:%02d:%02d" % (days, hours, minutes, seconds)
    return "%02d:%02d:%02d" % (hours, minutes, seconds)


def _reset_reason_text():
    try:
        reason = machine.reset_cause()
        for name, label in (
                ("PWRON_RESET", "GUC ACILISI"),
                ("HARD_RESET", "DONANIM"),
                ("WDT_RESET", "WATCHDOG"),
                ("DEEPSLEEP_RESET", "DERIN UYKU"),
                ("SOFT_RESET", "YAZILIM")):
            if hasattr(machine, name) and reason == getattr(machine, name):
                return label
        return str(reason)
    except Exception:
        return "-"


def _supply_voltage():
    try:
        # Pico 2 W'de WL_CS yuksekken GPIO29, VSYS/3 ADC girisine baglanir.
        wifi_cs = Pin(25, Pin.OUT)
        wifi_cs.value(1)
        time.sleep_us(200)
        adc = ADC(Pin(29))
        total = 0
        for _ in range(8):
            total += adc.read_u16()
        return (total / 8) * 3.3 * 3 / 65535
    except Exception:
        return None


def _last_error_text():
    try:
        f = open("last_error.txt")
        text = f.readline().strip()
        f.close()
        if not text:
            return "YOK"
        text = to_screen_text(text)
        return text[:22]
    except Exception:
        return "YOK"


def _ota_remote_version():
    if not is_online():
        return "v" + APP_VERSION
    try:
        status, text = https_get(
            "stellar-alfajores-1ac2b8.netlify.app", "/ota.json", 12)
        if status == 200 and text:
            return "v" + str(json.loads(text).get("version", "?")).strip()
    except Exception:
        pass
    return "v" + APP_VERSION


def _general_test_draw():
    lcd.fill(BG)
    lcd.text("GENEL TEST", 100, 7, TITLE_COL, 2)
    lcd.hline(0, 31, WIDTH, DARKGRAY)
    for i, label in enumerate(_GENERAL_TEST_ROWS):
        y = _GENERAL_TEST_ROW_Y + i * _GENERAL_TEST_ROW_STEP
        lcd.text(label, 8, y, GRAY, 1)
        lcd.text("BEKLE", 276, y, DARKGRAY, 1)
    lcd.fill_rect(0, 208, 158, 32, DARKGRAY)
    lcd.fill_rect(162, 208, 158, 32, DARKGRAY)
    lcd.vline(160, 208, 32, GRAY)
    lcd.text("YENILE", 61, 221, WHITE, 1)
    lcd.text("GERI", 230, 221, WHITE, 1)


def _general_test_result(index, value, color):
    y = _GENERAL_TEST_ROW_Y + index * _GENERAL_TEST_ROW_STEP
    lcd.fill_rect(176, y - 1, WIDTH - 184, 10, BG)
    value = str(value)
    lcd.text(value, WIDTH - len(value) * 6 - 8, y, color, 1)


def _general_test_run():
    gc.collect()
    _general_test_result(0, _uptime_text(), GREEN)

    cpu_temp = _cpu_temperature_c()
    if cpu_temp is None:
        _general_test_result(1, "OKUNAMADI", RED)
    else:
        _general_test_result(1, "%.1f C" % cpu_temp, GREEN)

    _general_test_result(2, _reset_reason_text(), GREEN)

    online = is_online()
    ip = "-"
    rssi = None
    if online:
        try:
            station = wlan if wlan is not None else network.WLAN(network.STA_IF)
            ip = station.ifconfig()[0]
            rssi = station.status("rssi")
        except Exception:
            pass
    _general_test_result(3, (str(rssi) + " dBm") if rssi is not None else "-",
                         GREEN)
    _general_test_result(4, ip, GREEN)
    ota_version = _ota_remote_version()
    _general_test_result(5, ota_version,
                         GREEN if ota_version.startswith("v") else RED)
    last_error = _last_error_text()
    _general_test_result(6, last_error, GREEN if last_error == "YOK" else RED)

    supply_v = _supply_voltage()
    voltage_text = "%.2f V" % supply_v if supply_v is not None else "HATA"
    _general_test_result(7, voltage_text,
                         RED if voltage_text == "HATA" else GREEN)

    try:
        cpu_mhz = machine_freq() // 1000000 if machine_freq is not None else 0
    except Exception:
        cpu_mhz = 0
    _general_test_result(8, (str(cpu_mhz) + " MHz") if cpu_mhz else "-",
                         GREEN)

    required = ("main.py", "clock_app.py", "gpt_stream.py", "sor_feature.py")
    try:
        names = os.listdir()
        files_ok = all(name in names for name in required)
    except Exception:
        files_ok = False
    gc.collect()
    try:
        ram_kb = gc.mem_free() // 1024
    except Exception:
        ram_kb = 0
    _general_test_result(9, str(ram_kb) + " KB",
                         GREEN)
    _general_test_result(10, "GPT-5.4", GREEN)
    _general_test_result(11, "4/4 OK" if files_ok else "EKSIK",
                         GREEN if files_ok else RED)
    refresh_hz = 1000.0 / UI_FRAME_MS if UI_FRAME_MS else 0
    _general_test_result(12, "%.1f Hz" % refresh_hz, GREEN)

    api_ms = None
    api_ok = False
    if online and OPENAI_API_KEY.strip():
        try:
            auth = "Authorization: Bearer " + OPENAI_API_KEY.strip() + "\r\n"
            started = time.ticks_ms()
            status, body = https_get(
                "api.openai.com", "/v1/models/gpt-5.4", 18, auth)
            api_ms = time.ticks_diff(time.ticks_ms(), started)
            api_ok = status == 200
            body = None
            auth = None
        except Exception:
            pass
    if api_ms is None:
        api_text = "-" if not online else "HATA"
    else:
        api_text = (str(api_ms) + " ms") if api_ok else "HATA"
    _general_test_result(13, api_text, RED if api_text == "HATA" else GREEN)
    gc.collect()


def run_general_test():
    _wait_touch_release()
    while True:
        _general_test_draw()
        _general_test_run()
        _wait_touch_release()
        while True:
            p = touch.read_fast()
            if p is None:
                time.sleep_ms(20)
                continue
            x, y = p
            if y >= 205:
                _wait_touch_release()
                if x >= WIDTH // 2:
                    return
                break


# ---- DIGER AYARLAR PANELI ----
_EBTN = [
    (53, 86, "DON"),
    (160, 86, "NET"),
    (267, 86, "TEST"),
    (107, 169, "NAMAZ"),
    (213, 169, "SOR"),
]


def _extra_hit(x, y):
    for i, (cx, cy, _lbl) in enumerate(_EBTN):
        dx = x - cx
        dy = y - cy
        if dx * dx + dy * dy <= 32 * 32:
            return i
    return None


def _extra_panel_draw():
    lcd.fill(BG)
    title = "DIGER AYARLAR"
    lcd.text(title, (WIDTH - len(title) * 12) // 2, 8, TITLE_COL, 2)
    lcd.hline(0, 33, WIDTH, DARKGRAY)

    _draw_rotate_icon(53, 86, screen_flip)
    _draw_circle_button(160, 86, 24, "NET", is_online(), "BAGLANTI")
    _draw_circle_button(267, 86, 24, "TEST", False, "GENEL")
    _draw_circle_button(107, 169, 24, "NM", prayer_mode_idx != 0, "NAMAZ")
    _draw_circle_button(213, 169, 24, "SOR", False, "GPT AYARI")

    lcd.fill_rect(0, 214, WIDTH, 26, DARKGRAY)
    lcd.hline(0, 214, WIDTH, GRAY)
    lcd.text("GERI", (WIDTH - 24) // 2, 224, WHITE, 1)


def run_extra_settings():
    global screen_flip
    _extra_panel_draw()
    _wait_touch_release()
    last = 0
    while True:
        p = touch.read_fast()
        if p is None:
            time.sleep_ms(20)
            continue
        now = time.ticks_ms()
        if time.ticks_diff(now, last) < TOUCH_DEBOUNCE_MS:
            continue
        last = now
        x, y = p
        if y >= 214:
            _wait_touch_release()
            return
        sel = _extra_hit(x, y)
        if sel is None:
            continue
        _wait_touch_release()
        if sel == 0:
            screen_flip = not screen_flip
            lcd.set_rotation(screen_flip)
            save_cfg()
            _extra_panel_draw()
        elif sel == 1:
            run_connection_diagnostics()
            _extra_panel_draw()
        elif sel == 2:
            run_general_test()
            _extra_panel_draw()
        elif sel == 3:
            run_prayer_settings()
            _extra_panel_draw()
        elif sel == 4:
            run_sor_settings()
            _extra_panel_draw()


# ---- SOR MENUSU: KLAVYE / HAZIR SORULAR ----



_SOR_PILL_Y0 = 44
_SOR_PILL_H = 26
_SOR_PILL_PAD = 10
_SOR_GAP_X = 8
_SOR_GAP_Y = 8
_SOR_MARGIN_X = 10








_SOR_TABS_Y0 = 6
_SOR_TABS_H = 24
_SOR_CONTENT_Y0 = _SOR_TABS_Y0 + _SOR_TABS_H + 6






_SOR_HAZIR_GERI_Y = 214
_SOR_HAZIR_GERI_H = 26




# ---- SOR: KLAVYE sekmesi (ust cubukta sadece sekmeler, GERI klavyede) ----
_SOR_IN_X = 4
_SOR_IN_Y = _SOR_CONTENT_Y0 + 2


_SOR_KB_GERI_X = 272
_SOR_KB_GERI_Y = KB_TOP + 3 * (KEY_H + 2)
_SOR_KB_GERI_W = WIDTH - _SOR_KB_GERI_X
















def open_sor():
    try:
        import sor_feature
        import sys
        return sor_feature.start(sys.modules[__name__])
    finally:
        try:
            del sys.modules["sor_feature"]
        except Exception:
            pass
        sor_feature = None
        release_answer_buffers()
        gc.collect()


def open_sor_safe():
    try:
        return open_sor()
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        try:
            safe_write_text("last_error.txt", "GPT: " + repr(exc) + "\n")
        except Exception:
            pass
        try:
            _gpt_wait_stop()
        except Exception:
            pass
        release_answer_buffers()
        show_status_screen("GPT HATASI", RED)
        time.sleep_ms(1400)
        draw_static()
        return None




_last_touch_deep = 0

def main_touch_read(now):
    global _last_touch_deep
    p = touch.read_fast()
    if p is not None:
        return p
    if face_idx == 1 and time.ticks_diff(now, _last_touch_deep) > 220:
        _last_touch_deep = now
        try:
            r = touch.read_screen()
            if r is not None:
                return (r[2], r[3])
        except Exception:
            pass
    return None


# ===================== ACILIS =====================
def boot_msg(msg, color=None):
    lcd.fill(BG)
    lcd.text(msg, (WIDTH - len(msg) * 12) // 2, HEIGHT // 2 - 8, color if color else FG, 2)


_boot_wait_step = 0


def boot_wait_tick():
    """WiFi beklerken acilis ekraninin alt cubugunu akici tutar."""
    global _boot_wait_step
    _watchdog_touch()
    bar_x = 70
    bar_y = 220
    inner_w = WIDTH - 144
    segment_w = 28
    travel = inner_w - segment_w
    phase = _boot_wait_step % max(1, travel * 2)
    pos = phase if phase <= travel else travel * 2 - phase
    lcd.fill_rect(bar_x + 2, bar_y + 2, inner_w, 2, DARKGRAY)
    lcd.fill_rect(bar_x + 2 + pos, bar_y + 2, segment_w, 2, TITLE_COL)
    _boot_wait_step += 5


def boot_anim():
    lcd.fill(BG)
    cx = WIDTH // 2
    cy = 92
    radius = 54
    title = "MASA SAATI"
    lcd.text(title, (WIDTH - len(title) * 12) // 2, 166, TITLE_COL, 2)
    subtitle = "PICO 2 W"
    lcd.text(subtitle, (WIDTH - len(subtitle) * 6) // 2, 194, GRAY, 1)


    bar_x = 70
    bar_y = 220
    bar_w = WIDTH - 140
    total_steps = 61
    lcd.rect(bar_x, bar_y, bar_w, 6, DARKGRAY)
    for k in range(36):
        a = k * 2.0 * _PI / 36.0
        major = (k % 3 == 0)
        inner = radius - (8 if major else 4)
        x0 = cx + int(inner * math.sin(a))
        y0 = cy - int(inner * math.cos(a))
        x1 = cx + int(radius * math.sin(a))
        y1 = cy - int(radius * math.cos(a))
        lcd.line(x0, y0, x1, y1, TITLE_COL if major else FG_DIM)
        fill = (k + 1) * (bar_w - 4) // total_steps
        lcd.fill_rect(bar_x + 2, bar_y + 2, fill, 2, TITLE_COL)
        time.sleep_ms(8)

    old = None
    for k in range(25):
        if old is not None:
            lcd.line(cx, cy, old[0], old[1], BG)
            lcd.line(cx + 1, cy, old[0] + 1, old[1], BG)
            lcd.line(cx, cy, old[2], old[3], BG)
            lcd.line(cx + 1, cy, old[2] + 1, old[3], BG)
        minute_a = k * 2.0 * _PI / 24.0
        hour_a = minute_a / 12.0 + 5.0 * _PI / 3.0
        mx = cx + int(39 * math.sin(minute_a))
        my = cy - int(39 * math.cos(minute_a))
        hx = cx + int(26 * math.sin(hour_a))
        hy = cy - int(26 * math.cos(hour_a))
        lcd.line(cx, cy, mx, my, FG)
        lcd.line(cx + 1, cy, mx + 1, my, FG)
        lcd.line(cx, cy, hx, hy, TITLE_COL)
        lcd.line(cx + 1, cy, hx + 1, hy, TITLE_COL)
        old = (mx, my, hx, hy)
        fill = (37 + k) * (bar_w - 4) // total_steps
        lcd.fill_rect(bar_x + 2, bar_y + 2, fill, 2, TITLE_COL)
        time.sleep_ms(16)
    lcd.circle(cx, cy, 4, TITLE_COL)
    time.sleep_ms(180)


def main():
    global spi, lcd, touch, bl_pwm
    global last_sec, last_day, colon_on, face_idx, weather_idx
    global USE_24H, bright_idx, bright_value, mode_idx, screen_flip
    global _dimmed_today, _brightened_today

    spi = SPI(1, baudrate=LCD_BAUD, polarity=0, phase=0,
              sck=Pin(LCD_SCK), mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))
    lcd = ST7789(spi, LCD_CS, LCD_DC, LCD_RST, LCD_BL, WIDTH, HEIGHT)
    touch = XPT2046(spi, TP_CS)

    load_cfg()
    load_touch_cal()
    load_wifi()
    wifi_boot_attempts = 0
    try:
        bl_pwm = PWM(Pin(LCD_BL))
        bl_pwm.freq(1000)
        bl_pwm.duty_u16(bright_value)
    except Exception:
        bl_pwm = None
    if screen_flip:
        lcd.set_rotation(True)

    watchdog_start()

    if anim_on:
        boot_anim()
    else:
        boot_msg("MASA SAATI", TITLE_COL)
        time.sleep_ms(600)

    wifi_boot_attempts = wifi_boot_connect()
    boot_network_synced = False
    if is_online():
        boot_wait_tick()
        ntp_sync()
        boot_wait_tick()
        geo_locate()
        boot_wait_tick()
        if prayer_mode_idx != 0:
            prayer_sync()
        boot_wait_tick()
        sunset_sync()
        boot_wait_tick()
        weather_forecast_fetch()
        boot_network_synced = True

    draw_static()

    last_sec = -1
    last_day = -1
    press_start = None
    press_last = None
    press_t0 = 0
    long_done = False
    sec_ms = time.ticks_ms()
    last_face_anim = 0
    last_weather_anim = 0
    last_status_min = -1
    last_touch_poll = 0
    last_wifi_retry = time.ticks_ms()
    stable_boot_started = last_wifi_retry
    last_gc = last_wifi_retry
    was_online = is_online()
    network_sync_stage = -1 if boot_network_synced else (0 if was_online else -1)

    while True:
        now = time.ticks_ms()
        _watchdog_touch()
        _ota_confirm_boot_if_stable(stable_boot_started, now)

        if (press_start is None and
                time.ticks_diff(now, last_touch_poll) < TOUCH_IDLE_POLL_MS):
            p = None
        else:
            p = main_touch_read(now)
            last_touch_poll = now
        touch_active = (p is not None)

        if touch_active:
            if press_start is None:
                press_start = p
                press_t0 = now
                long_done = False
            press_last = p

            stable = (abs(p[0] - press_start[0]) < 25 and
                      abs(p[1] - press_start[1]) < 25)
            held = time.ticks_diff(now, press_t0) > LONG_PRESS_MS

            if not long_done and press_start[1] < BTN_Y - 4 and stable and held:

                face_idx = (face_idx + 1) % FACE_COUNT
                save_cfg()
                wipe_transition()
                draw_static()
                long_done = True

        else:
            if press_start is not None and not long_done:
                sx, sy = press_start
                ex, ey = press_last
                dx = ex - sx
                dy = ey - sy
                if abs(dx) >= 50 and abs(dx) > abs(dy) + 8:
                    face_idx = (face_idx + (1 if dx < 0 else -1)) % FACE_COUNT
                    save_cfg()
                    wipe_transition()
                    draw_static()
                elif abs(dx) < 22 and abs(dy) < 22 and sy < 28:

                    if sx >= OTA_TOP_HIT_X0:
                        _run_ota_from_top()
                        draw_static()
                    elif not is_online():
                        if sx >= TOPBTN_HIT_X0:
                            run_set()
                            draw_static()
                        else:
                            run_wifi_setup()
                            draw_static()
                elif abs(dx) < 22 and abs(dy) < 22 and sy < BTN_Y - 4 and face_idx == 2:


                    weather_idx = 1 if weather_idx == 2 else 2
                    weather_init()
                    save_cfg()
                    draw_static()
                elif abs(dx) < 22 and abs(dy) < 22 and sy >= BTN_Y - 4:
                    slot = sx * 3 // WIDTH
                    if slot == 0:
                        run_all_settings()
                        draw_static()
                    elif slot == 1:
                        run_weather_forecast()
                        draw_static()
                    else:
                        open_sor_safe()
            press_start = None
            press_last = None
            long_done = False

        now = time.ticks_ms()
        lt = time.localtime()
        sec = lt[5]
        if sec != last_sec:
            last_sec = sec
            colon_on = not colon_on
            sec_ms = now
            day_changed = (lt[2] != last_day)
            face_update(lt, day_changed)
            if day_changed:
                last_day = lt[2]
                _dimmed_today = False
                _brightened_today = False
            if lt[4] != last_status_min:
                last_status_min = lt[4]
                draw_status()
            online = is_online()
            if online and not was_online:
                network_sync_stage = 0
            ran_network_stage = False
            if online and network_sync_stage >= 0:
                ran_network_stage = True
                if network_sync_stage == 0:
                    ntp_sync()
                elif network_sync_stage == 1:
                    geo_locate()
                elif network_sync_stage == 2:
                    if prayer_mode_idx != 0:
                        prayer_sync()
                elif network_sync_stage == 3:
                    sunset_sync()
                elif network_sync_stage == 4:
                    weather_forecast_fetch()
                network_sync_stage += 1
                if network_sync_stage > 4:
                    network_sync_stage = -1
                draw_status()
            boot_retry = (wifi_boot_attempts < WIFI_BOOT_RETRY_COUNT and
                          time.ticks_diff(now, last_wifi_retry) >=
                          WIFI_BOOT_RETRY_MS)
            normal_retry = (wifi_boot_attempts >= WIFI_BOOT_RETRY_COUNT and
                            time.ticks_diff(now, last_wifi_retry) >=
                            WIFI_RETRY_MS)
            if WIFI_SSID and not online and (boot_retry or normal_retry):
                last_wifi_retry = now
                wifi_reconnect_start(WIFI_SSID, WIFI_PASS)
                draw_status()
                if wifi_boot_attempts < WIFI_BOOT_RETRY_COUNT:
                    wifi_boot_attempts += 1
            if ntp_ok and time.ticks_diff(now, last_ntp) > NTP_EVERY_MS:
                ntp_sync()
                draw_status()
            if prayer_mode_idx != 0 and network_sync_stage < 0 and not ran_network_stage:
                if online and prayer_day_key != _prayer_key(lt):
                    if prayer_sync():
                        draw_status()
                elif online and time.ticks_diff(now, last_prayer_sync) > PRAYER_EVERY_MS:
                    if prayer_sync():
                        draw_status()
            if (online and network_sync_stage < 0 and not ran_network_stage
                    and _sunset_day_key != _prayer_key(lt)):
                sunset_sync()
            weather_age = time.ticks_diff(now, _weather_cache_ms)
            weather_retry_age = time.ticks_diff(now, _weather_last_attempt)
            if (online and network_sync_stage < 0 and not ran_network_stage and
                    ((not _weather_cache_days and
                      weather_retry_age >= WEATHER_RETRY_MS) or
                     (_weather_cache_days and
                      weather_age >= WEATHER_REFRESH_MS))):
                weather_forecast_fetch()
                if face_idx == 1:
                    analog_prayer_panel(lt, True)
            was_online = online
            if (DIM_AT_MIN >= 0 and not _dimmed_today
                    and lt[3] * 60 + lt[4] >= DIM_AT_MIN):


                _dimmed_today = True
                if bright_value != BRIGHT_LEVELS[-1]:
                    bright_idx = len(BRIGHT_LEVELS) - 1
                    bright_value = BRIGHT_LEVELS[bright_idx]
                    if bl_pwm is not None:
                        bl_pwm.duty_u16(bright_value)
                    save_cfg()
            if (BRIGHTEN_AT_MIN >= 0 and not _brightened_today
                    and lt[3] * 60 + lt[4] >= BRIGHTEN_AT_MIN):


                _brightened_today = True
                if bright_value != BRIGHT_LEVELS[0]:
                    bright_idx = 0
                    bright_value = BRIGHT_LEVELS[bright_idx]
                    if bl_pwm is not None:
                        bl_pwm.duty_u16(bright_value)
                    save_cfg()
        elif anim_on:
            if time.ticks_diff(now, last_face_anim) >= UI_FRAME_MS:
                last_face_anim = now
                frac = time.ticks_diff(now, sec_ms) / 1000.0
                if frac < 0:
                    frac = 0.0
                if frac > 0.999:
                    frac = 0.999
                face_anim(lt, frac)

        if face_idx == 2 and time.ticks_diff(now, last_weather_anim) >= weather_interval_ms():
            last_weather_anim = now
            weather_step()

        if WIFI_SSID and not was_online:
            _wifi_wait_step()

        if time.ticks_diff(now, last_gc) >= GC_EVERY_MS:
            gc.collect()
            last_gc = now

        time.sleep_ms(MAIN_LOOP_MS)


def run_clock():
    try:
        main()
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        safe_write_text("last_error.txt", repr(exc) + "\n")
        try:
            lcd.fill(BG)
            lcd.text("HATA - YENIDEN BASLIYOR", 82, 112, RED, 1)
        except Exception:
            pass
        time.sleep_ms(1800)
        if machine_reset is not None:
            machine_reset()
        raise


if __name__ == "__main__":
    run_clock()
