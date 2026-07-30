# -*- coding: utf-8 -*-
# Raspberry Pi Pico 2 W + ST7789 320x240 dokunmatik ekran ile MASA SAATI
# Ayni kart ve ekran (Waveshare Pico-ResTouch-LCD tarzi). Thonny'de main.py olarak kaydet.
#
# OZELLIKLER:
#  - Buyuk 7-segment HH:MM, yanip sonen iki nokta, altinda saniye cubugu
#  - Gun + tarih (Turkce, ASCII)
#  - WiFi varsa NTP ile otomatik saat ayari (internetten dogru saat)
#  - Dokunmatik: AYARLAR/KOYU-ACIK/GPT tuslari altta
#    her zaman gorunur.
#    Saat bicimi sabit 24 saattir.
#
# ==== KULLANICI AYARLARI ====
WIFI_SSID = ""          # WiFi adi (bos birakirsan internet kullanmaz, elle ayar yaparsin)
WIFI_PASS = ""          # WiFi sifresi
TZ_OFFSET = 3           # Saat dilimi farki (Turkiye = UTC+3)
USE_24H = True          # True: 24 saat (14:30), False: 12 saat (02:30)
NTP_EVERY_MS = 3600000  # Her 1 saatte bir internetten tekrar saat al
WIFI_RETRY_MS = 60000    # Baglanti koparsa her 1 dakikada bir tekrar dene
GC_EVERY_MS = 300000     # Uzun calismalarda bellek parcalanmasini azalt

# Il (bolge) IP uzerinden otomatik tespit edilir (SOR cevaplari ve namaz
# vakitleri icin, ekranda gosterilmez). Yanlis cikarsa kendi ilini
# asagiya yaz; bos birakirsan otomatik tespit edilen kullanilir.
MANUAL_LOCATION = ""    # ORNEK: "Mugla"


# ==== SOR (ChatGPT) AYARLARI ====
OPENAI_API_KEY = ""
QA_MODEL = "gpt-5-nano"
WEB_SEARCH_MODEL = "gpt-5.4-nano"
WEB_MAX_TOKENS = 350
WEB_RETRY_TOKENS = 700
GPT_RETRY_COUNT = 1                                  # gecici hatada bir kez daha dene
GPT_RETRY_DELAY_MS = 900
GPT_RETRY_OUTPUT_BUDGET = 8192
APP_VERSION = "1.0.17"
OTA_MANIFEST_URL = ("https://raw.githubusercontent.com/"
                    "ysnkrt/masa-saati-ota/main/ota.json")
OTA_MAX_BYTES = 350000

USER_COUNTRY = "TR"
USER_CITY = "Istanbul"
USER_REGION = "Istanbul"
USER_LAT = None         # gun batimi hesabi icin (geo_locate ile doldurulur)
USER_LON = None
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
                 "kendin biliyormus gibi dogrudan soyle. "
                 "Cevabinin en sonunda, sadece verdigin bilginin hangi yila "
                 "ait oldugunu kisa bir cumleyle belirt (kaynak degil, sadece yil).")
WEB_SYSTEM_PROMPT = (
    "Turkce ve yalnizca duz metin cevap ver. En fazla 1-3 kisa cumle kullan. "
    "Kullaniciya kesinlikle soru sorma veya secenek sunma. Belirsiz bir haber "
    "sorusunda Turkiye ile ilgili en onemli guncel haberi secip cevapla. "
    "Guncel veriyi bulamazsan erisemiyorum veya dogrulayamiyorum deme; web "
    "aramasinda buldugun en yeni sonucu tarihini belirterek dogrudan ver. "
    "Mac ve fikstur sorularini sadece Super Lig ile sinirlama; UEFA, Avrupa "
    "ligleri, milli maclar ve Turkiye liglerinden en onemli maclari birlikte ver. "
    "URL, site veya kaynak adi yazma. Bugunun tarihi %s. En yeni tarihli "
    "guvenilir veriyi kullan; farkli tarihler varsa en guncelini sec. "
    "Son cumlede verinin tam tarihini belirt.")
MAX_TOKENS = 450
# ============================

# SOR cevap ayarlari (soru ekranindaki AYAR tusundan degisir, kalici)
# yazi boyutu profilleri: (harf_gen, harf_yuk, ilerleme, satir_yuk)
SIZE_PROFILES = [(10, 14, 11, 20), (8, 11, 9, 16), (6, 8, 7, 12)]
SIZE_NAMES = ["BUYUK", "ORTA", "KUCUK"]
# cevap uzunlugu: (ad, token, prompt eki)
LEN_PROFILES = [
    ("UZUN", 900, "Cevabini detayli ve kapsamli ver."),
    ("NORMAL", 350, "Cevabini orta uzunlukta ozetle."),
    ("KISA", 200, "Cevabini cok kisa, 1-2 cumlede ver."),
]
ans_size_idx = 1     # ORTA
ans_len_idx = 1      # NORMAL
anim_on = True       # saat animasyonlari
UI_FRAME_MS = 80     # animasyon yenileme araligi
MAIN_LOOP_MS = 12    # ana dongu beklemesi
TOUCH_IDLE_POLL_MS = 22
LONG_PRESS_MS = 650
TOUCH_DEBOUNCE_MS = 140

# HAVA ANIMASYONU: sadece BUYUK YAZI (HH:MM:SS) ekraninda calisir.
# 1=kar, 2=yagmur. Buyuk dijital ekrana dokununca 1/2 arasinda gecis yapar.
weather_idx = 2

# ==== NAMAZ VAKITLERI ====
# HIZLI AYAR > NM menusu: KAPALI / YAKIN / HEPSI
PRAYER_CITY = "Istanbul"
PRAYER_COUNTRY = "Turkey"
PRAYER_METHOD = 13          # Turkiye/Diyanet hesabi
PRAYER_EVERY_MS = 21600000  # 6 saatte bir tekrar dene
PRAYER_MODE_NAMES = ["KAPALI", "YAKIN", "HEPSI"]
prayer_mode_idx = 1         # 0=kapali, 1=en yakin, 2=tum vakitler
PRAYER_SIZE_NAMES = ["NORMAL", "BUYUK"]
prayer_size_idx = 0         # 0=normal, 1=buyuk
PRAYER_THICK_NAMES = ["INCE", "ORTA", "KALIN"]
prayer_thick_idx = 1        # 0=ince, 1=orta, 2=kalin
PRAYER_GAP_NAMES = ["SIK", "NORMAL", "GENIS"]
prayer_gap_idx = 1          # HEPSI modunda vakitler arasi bosluk

from machine import Pin, SPI, PWM
import time
import gc
import math

try:
    import os
except Exception:
    import uos as os
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

LCD_BAUD = 24000000     # ekran cizim hizi; ekran bozulursa 16000000 yap
TOUCH_BAUD = 2000000

WIDTH = 320
HEIGHT = 240

# ---- Renkler (RGB565) ----
BLACK = 0x0000
WHITE = 0xFFFF
GRAY = 0x8410
DGRAY = 0x2104          # sonuk "hayalet" segment rengi
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
LGRAY = 0xC618          # acik gri (acik modda "soluk/hayalet" icin)

# Ekran modu: saat, ust/alt cubuk ve tum ana ekran bu renklerle cizilir.
# KOYU: zemin siyah, beyaz. ACIK: zemin beyaz, "beyaz" yerler siyah.
MODE_NAMES = ["KOYU", "ACIK"]
mode_idx = 0            # 0=KOYU (varsayilan) 1=ACIK

BG = BLACK              # ana ekran zemin rengi (moda gore guncellenir)
FG = WHITE              # ana ekran (saat + ust/alt cubuk) on plan rengi
FG_DIM = DGRAY          # "hayalet/bos" ogeler (dolmamis saniye cizgisi vb.)
RAIN_COL = CYAN         # yagmur damlasi rengi (moda gore okunur olsun)
RING_FULL = WHITE       # analog: dolmus (gecmis) saniye cizgisi
RING_EMPTY = DARKGRAY   # analog: dolmamis saniye cizgisi (soluk ama gorunur)
TAB_UNSEL = DARKGRAY    # SOR sekmelerinde secili OLMAYAN sekmenin zemini
TITLE_COL = CYAN        # panel basliklari/durum yazilari (moda gore okunur)
LOCK_CLOSED_COL = GRAY  # wifi listesinde "kilitli" (bilinmeyen) ag ikonu


def apply_mode():
    global BG, FG, FG_DIM, RAIN_COL, RING_FULL, RING_EMPTY, TAB_UNSEL
    global TITLE_COL, LOCK_CLOSED_COL
    if mode_idx == 1:
        BG = WHITE
        FG = BLACK
        FG_DIM = LGRAY      # beyaz zeminde bos ogeler acik gri
        RAIN_COL = BLACK    # beyaz zeminde siyah yagmur
        RING_FULL = BLACK
        RING_EMPTY = LGRAY
        # ACIK modda secili sekme (FG=siyah) ile secili olmayan sekme
        # birbirine cok yakin koyulukta olmasin diye secili olmayan
        # daha acik gri yapilir.
        TAB_UNSEL = GRAY
        TITLE_COL = BLACK   # acik modda basliklar siyah
        LOCK_CLOSED_COL = BLACK
    else:
        BG = BLACK
        FG = WHITE
        FG_DIM = DGRAY
        RAIN_COL = CYAN
        RING_FULL = WHITE
        RING_EMPTY = DARKGRAY
        TAB_UNSEL = DARKGRAY
        TITLE_COL = CYAN
        LOCK_CLOSED_COL = GRAY
    _rebuild_ans_zero_buffers()   # SOR cevap zeminini yeni BG'ye gore yenile

# Parlaklik kademeleri (PWM duty 0-65535)
BRIGHT_LEVELS = [65535, 49151, 32768, 16384, 655]
BRIGHT_NAMES = ["%100", "%75", "%50", "%25", "%1"]
bright_idx = 0
BRIGHT_MIN = 655       # yaklasik %1; ekran tamamen kapanmaz
bright_value = BRIGHT_LEVELS[bright_idx]

# Ekrani ters cevirme (180 derece)
screen_flip = False

# Saat modeli (sola/saga kaydirarak degisir): 0=dijital 1=analog 2=buyuk yazi 3=nabiz
face_idx = 0
FACE_COUNT = 4

# ---- Dokunmatik kalibrasyonu ----
RAW_X_MIN = 300
RAW_X_MAX = 3900
RAW_Y_MIN = 300
RAW_Y_MAX = 3900


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
# Kucuk harfler ve ek semboller (wifi sifresi girisi icin)
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
        # flip=True -> 180 derece dondur
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
        # Dolu daireyi piksel piksel degil, yatay satirlar halinde ciz.
        rr = r * r
        for yy in range(-r, r + 1):
            xx = r
            y2 = yy * yy
            while xx > 0 and xx * xx + y2 > rr:
                xx -= 1
            self.fill_rect(cx - xx, cy + yy, xx * 2 + 1, 1, color)

    def ring(self, cx, cy, r, color):
        # sadece cember cizgisi (icini doldurmaz) - hizli
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
        if screen_flip:                 # 180 derece donukse dokunmayi da cevir
            x = WIDTH - 1 - x
            y = HEIGHT - 1 - y
        return clamp(x, 0, WIDTH - 1), clamp(y, 0, HEIGHT - 1)

    def read_raw(self):
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
        self.spi.init(baudrate=TOUCH_BAUD, polarity=0, phase=0)
        try:
            xs = []; ys = []
            for _ in range(5):
                x = self.read_axis(0xD0)
                y = self.read_axis(0x90)
                z1 = self.read_axis(0xB0)
                if z1 > 50 and 300 <= x <= 3800 and 300 <= y <= 3800:
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


# Cevap ekrani: secilebilir punto (BUYUK/ORTA/KUCUK), parmakla kaydirma
_EMPTY = []
ANS_TOP = 24
ANS_BOTTOM = 206

# Yalnizca secili cevap boyutunun glif tablosunu RAM'de tut.
def _build_glyph_table(idx):
    _AGWp, _AGHp, _AADVp, _LHp = SIZE_PROFILES[idx]
    _tbl = {}
    for _ch in FONT:
        _g = FONT[_ch]
        _pts = []
        for _dy in range(_AGHp):
            _sy = _dy * 7 // _AGHp
            _row = _g[_sy]
            for _dx in range(_AGWp):
                _sx = _dx * 5 // _AGWp
                if _row[_sx] == "1":
                    _pts.append((_dx, _dy))
        _tbl[_ch] = _pts
    return _tbl

_DEFAULT_ANS_IDX = 1
_GLYPH_TABLES = [None] * len(SIZE_PROFILES)
_GLYPH_TABLES[_DEFAULT_ANS_IDX] = _build_glyph_table(_DEFAULT_ANS_IDX)
_BUFS = [None] * len(SIZE_PROFILES)
_ZEROS = [None] * len(SIZE_PROFILES)
_DEFAULT_ANS_BYTES = WIDTH * SIZE_PROFILES[_DEFAULT_ANS_IDX][3] * 2
_BUFS[_DEFAULT_ANS_IDX] = bytearray(_DEFAULT_ANS_BYTES)
_ZEROS[_DEFAULT_ANS_IDX] = bytearray(_DEFAULT_ANS_BYTES)

# aktif boyut degiskenleri (apply_ans_size ile ayarlanir)
_AADV = 9
ANS_LINE_H = 16
ANS_CHARS = (WIDTH - 8) // _AADV
ANS_VISIBLE = (ANS_BOTTOM - ANS_TOP) // ANS_LINE_H
_AGLYPH = _GLYPH_TABLES[_DEFAULT_ANS_IDX]
_ANS_BUF = _BUFS[_DEFAULT_ANS_IDX]
_ANS_ZERO = _ZEROS[_DEFAULT_ANS_IDX]


def _fill_answer_background(zero):
    if zero is None:
        return
    hi = BG >> 8
    lo = BG & 0xFF
    chunk = bytes([hi, lo]) * 32
    chunk_len = len(chunk)
    for start in range(0, len(zero), chunk_len):
        end = min(start + chunk_len, len(zero))
        zero[start:end] = chunk[:end - start]


def _rebuild_ans_zero_buffers():
    # SOR cevap satirinin zeminini yeni temaya gore yerinde boya.
    global _ANS_ZERO
    for zero in _ZEROS:
        _fill_answer_background(zero)
    active = _ZEROS[ans_size_idx % len(SIZE_PROFILES)]
    if active is not None:
        _ANS_ZERO = active


def release_answer_buffers():
    global _ANS_BUF, _ANS_ZERO
    _ANS_BUF = None
    _ANS_ZERO = None
    for i in range(len(_BUFS)):
        _BUFS[i] = None
        _ZEROS[i] = None
    gc.collect()


def apply_ans_size(idx):
    global _AADV, ANS_LINE_H, ANS_CHARS, ANS_VISIBLE, _AGLYPH, _ANS_BUF, _ANS_ZERO
    idx = idx % len(SIZE_PROFILES)
    AGW, AGH, AADV, LH = SIZE_PROFILES[idx]
    if _GLYPH_TABLES[idx] is None:
        _AGLYPH = None
        for i in range(len(_GLYPH_TABLES)):
            if i != idx:
                _GLYPH_TABLES[i] = None
        gc.collect()
        _GLYPH_TABLES[idx] = _build_glyph_table(idx)
    if _BUFS[idx] is None or _ZEROS[idx] is None:
        release_answer_buffers()
        size = WIDTH * LH * 2
        _BUFS[idx] = bytearray(size)
        _ZEROS[idx] = bytearray(size)
        _fill_answer_background(_ZEROS[idx])
    _AADV = AADV
    ANS_LINE_H = LH
    ANS_CHARS = (WIDTH - 8) // AADV
    ANS_VISIBLE = (ANS_BOTTOM - ANS_TOP) // LH
    _AGLYPH = _GLYPH_TABLES[idx]
    _ANS_BUF = _BUFS[idx]
    _ANS_ZERO = _ZEROS[idx]


def render_answer_line(text, screen_y):
    buf = _ANS_BUF
    buf[:] = _ANS_ZERO
    w = WIDTH
    cx = 4
    limit = w - _AADV
    th = FG
    hi = th >> 8
    lo = th & 0xFF
    for ch in text:
        pts = _AGLYPH.get(ch)
        if pts is None:
            pts = _AGLYPH.get(ch.upper(), _EMPTY)
        for (dx, dy) in pts:
            idx = (dy * w + cx + dx) * 2
            buf[idx] = hi
            buf[idx + 1] = lo
        cx += _AADV
        if cx > limit:
            break
    lcd.set_window(0, screen_y, w - 1, screen_y + ANS_LINE_H - 1)
    lcd.dc.value(1)
    lcd.cs.value(0)
    lcd.spi.write(buf)
    lcd.cs.value(1)


def draw_answer_frame():
    lcd.fill(BG)
    lcd.text("GPT:", 4, 4, GREEN, 2)
    lcd.fill_rect(0, 210, 158, 30, BLUE)
    lcd.rect(0, 210, 158, 30, GRAY)
    lcd.text("GERI", 56, 219, WHITE, 1)
    lcd.fill_rect(162, 210, 158, 30, GREEN)
    lcd.rect(162, 210, 158, 30, GRAY)
    lcd.text("YENI SORU", 192, 219, BLACK, 1)


def draw_answer_text(lines, offset):
    n = len(lines)
    i = offset
    for row in range(ANS_VISIBLE):
        screen_y = ANS_TOP + row * ANS_LINE_H
        render_answer_line(lines[i] if i < n else "", screen_y)
        i += 1
    if n > ANS_VISIBLE:
        track_h = ANS_BOTTOM - ANS_TOP
        bar_h = max(12, track_h * ANS_VISIBLE // n)
        max_off = n - ANS_VISIBLE
        bar_y = ANS_TOP + (track_h - bar_h) * offset // max_off
        lcd.fill_rect(WIDTH - 4, ANS_TOP, 3, track_h, DARKGRAY)
        lcd.fill_rect(WIDTH - 4, bar_y, 3, bar_h, CYAN)


def show_answer(lines):
    max_off = len(lines) - ANS_VISIBLE
    if max_off < 0:
        max_off = 0
    offset = 0
    draw_answer_frame()
    draw_answer_text(lines, offset)
    last_y = None
    accum = 0
    while True:
        res = touch.read_fast()
        if res is None:
            last_y = None
            accum = 0
            time.sleep_ms(5)
            continue
        x, y = res
        if last_y is None:
            if y >= 210:
                time.sleep_ms(120)
                return "back" if x < 160 else "new"
            last_y = y
            continue
        dy = y - last_y
        last_y = y
        accum += -dy
        changed = False
        while accum >= ANS_LINE_H and offset < max_off:
            offset += 1; accum -= ANS_LINE_H; changed = True
        while accum <= -ANS_LINE_H and offset > 0:
            offset -= 1; accum += ANS_LINE_H; changed = True
        if accum > ANS_LINE_H:
            accum = ANS_LINE_H
        elif accum < -ANS_LINE_H:
            accum = -ANS_LINE_H
        if changed:
            draw_answer_text(lines, offset)


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
            n = int(data[i:j], 16)
        except ValueError:
            break
        if n == 0:
            break
        start = j + 2
        out.extend(data[start:start + n])
        i = start + n + 2
    return out


def https_post(host, path, api_key, body_str, timeout=45):
    body = body_str.encode("utf-8")
    body_str = None
    s = None
    ss = None
    raw = None
    try:
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
        req = ("POST " + path + " HTTP/1.1\r\n"
               "Host: " + host + "\r\n"
               "Authorization: Bearer " + api_key + "\r\n"
               "Content-Type: application/json\r\n"
               "Content-Length: " + str(len(body)) + "\r\n"
               "Connection: close\r\n\r\n")
        ss.write(req.encode("utf-8"))
        ss.write(body)
        body = None
        raw = bytearray()
        poller = None
        if select is not None:
            try:
                poller = select.poll()
                poller.register(ss, select.POLLIN)
            except Exception:
                poller = None
        read_started = time.ticks_ms()
        read_errors = 0
        while True:
            if poller is not None:
                try:
                    ready = poller.poll(90)
                except Exception:
                    poller = None
                    ready = None
                if poller is not None and not ready:
                    _gpt_wait_step()
                    if time.ticks_diff(time.ticks_ms(), read_started) >= timeout * 1000:
                        break
                    continue
            try:
                d = ss.read(512)
            except Exception:
                read_errors += 1
                if (poller is not None and read_errors < 200 and
                        time.ticks_diff(time.ticks_ms(), read_started) < timeout * 1000):
                    _gpt_wait_step()
                    time.sleep_ms(10)
                    continue
                raise
            if not d:
                break
            read_errors = 0
            raw.extend(d)
            _gpt_wait_step()
        he = _buffer_find(raw, b"\r\n\r\n")
        if he < 0:
            return 0, ""
        head = bytes(raw[:he])
        del raw[:he + 4]
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
        body = None
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



def https_get(host, path, timeout=25):
    if socket is None or ssl is None:
        return 0, ""
    s = None
    ss = None
    raw = None
    try:
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
               "Connection: close\r\n\r\n")
        ss.write(req.encode("utf-8"))
        raw = bytearray()
        while True:
            d = ss.read(512)
            if not d:
                break
            raw.extend(d)
        he = _buffer_find(raw, b"\r\n\r\n")
        if he < 0:
            return 0, ""
        head = bytes(raw[:he])
        del raw[:he + 4]
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


OTA_RAW_FILE = "main.py.ota.raw"
OTA_READY_FILE = "main.py.ota"
OTA_BACKUP_FILE = "main.py.bak"
OTA_STATE_FILE = "ota_state.txt"


def _ota_parse_url(url):
    prefix = "https://"
    if not url.startswith(prefix):
        return None, None
    rest = url[len(prefix):]
    slash = rest.find("/")
    if slash < 0:
        return rest, "/"
    return rest[:slash], rest[slash:]


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


def ota_check_manifest():
    host, path = _ota_parse_url(OTA_MANIFEST_URL)
    if not host:
        return None, "OTA ADRESI GECERSIZ"
    try:
        gc.collect()
        status, text = https_get(host, path, 20)
    except Exception as exc:
        return None, "OTA BAGLANTI: " + str(exc)
    if status != 200:
        return None, "OTA SUNUCU KODU " + str(status)
    try:
        data = json.loads(text)
        version = str(data["version"]).strip()
        url = str(data["url"]).strip()
        sha256 = str(data["sha256"]).strip().lower()
        raw_notes = data.get("notes", [])
    except Exception:
        return None, "OTA BILGISI GECERSIZ"
    if not version or not url.startswith("https://") or len(sha256) != 64:
        return None, "OTA ALANLARI EKSIK"
    if isinstance(raw_notes, str):
        raw_notes = [raw_notes]
    notes = []
    for item in raw_notes:
        note = str(item).strip()
        if note:
            notes.append(note)
        if len(notes) >= 4:
            break
    return {"version": version, "url": url, "sha256": sha256,
            "notes": notes}, None


def _ota_digest_hex(hasher):
    return "".join("%02x" % b for b in hasher.digest())


def _ota_draw_progress(done, total):
    x = 28
    y = 146
    width = WIDTH - 56
    lcd.rect(x, y, width, 14, GRAY)
    inner = width - 4
    fill = done * inner // total if total > 0 else (done // 1024) % inner
    if fill < 0:
        fill = 0
    if fill > inner:
        fill = inner
    lcd.fill_rect(x + 2, y + 2, fill, 10, GREEN)
    if fill < inner:
        lcd.fill_rect(x + 2 + fill, y + 2, inner - fill, 10, DARKGRAY)
    text = "%d KB" % (done // 1024)
    lcd.fill_rect(0, 170, WIDTH, 14, BG)
    lcd.text(text, (WIDTH - len(text) * 6) // 2, 173, FG, 1)


def ota_download(url, expected_sha):
    if hashlib is None:
        return False, "SHA256 MODULU YOK"
    host, path = _ota_parse_url(url)
    if not host:
        return False, "DOSYA ADRESI GECERSIZ"
    raw = None
    ss = None
    f = None
    try:
        gc.collect()
        try:
            os.remove(OTA_RAW_FILE)
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
            ss = ssl.wrap_socket(raw, server_hostname=host)
        except TypeError:
            ss = ssl.wrap_socket(raw)
        req = ("GET " + path + " HTTP/1.1\r\n"
               "Host: " + host + "\r\n"
               "User-Agent: masa-saati/" + APP_VERSION + "\r\n"
               "Accept: application/octet-stream\r\n"
               "Connection: close\r\n\r\n")
        ss.write(req.encode("utf-8"))
        status_line = ss.readline()
        try:
            status = int(status_line.split(b" ")[1])
        except Exception:
            status = 0
        chunked = False
        expected_size = 0
        while True:
            line = ss.readline()
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
            return False, "GUNCELLEME COK BUYUK"

        f = open(OTA_RAW_FILE, "wb")
        hasher = hashlib.sha256()
        done = 0
        shown = -4096
        if chunked:
            while True:
                line = ss.readline()
                if not line:
                    raise OSError("chunk basligi yok")
                size = int(line.split(b";", 1)[0].strip(), 16)
                if size == 0:
                    break
                remaining = size
                while remaining > 0:
                    block = ss.read(min(512, remaining))
                    if not block:
                        raise OSError("dosya yarim kaldi")
                    done += len(block)
                    if done > OTA_MAX_BYTES:
                        raise OSError("dosya cok buyuk")
                    f.write(block)
                    hasher.update(block)
                    remaining -= len(block)
                    if done - shown >= 4096:
                        _ota_draw_progress(done, expected_size)
                        shown = done
                ss.read(2)
        else:
            while True:
                block = ss.read(512)
                if not block:
                    break
                done += len(block)
                if done > OTA_MAX_BYTES:
                    raise OSError("dosya cok buyuk")
                f.write(block)
                hasher.update(block)
                if done - shown >= 4096:
                    _ota_draw_progress(done, expected_size)
                    shown = done
        try:
            f.flush()
        except Exception:
            pass
        f.close()
        f = None
        _ota_draw_progress(done, expected_size if expected_size else done)
        if done < 1024:
            return False, "GUNCELLEME DOSYASI COK KUCUK"
        if expected_size and done != expected_size:
            return False, "GUNCELLEME DOSYASI YARIM"
        if _ota_digest_hex(hasher) != expected_sha:
            return False, "SHA256 DOGRULANAMADI"
        return True, None
    except Exception as exc:
        return False, "INDIRME HATASI: " + str(exc)
    finally:
        if f is not None:
            try:
                f.close()
            except Exception:
                pass
        if ss is not None:
            try:
                ss.close()
            except Exception:
                pass
        elif raw is not None:
            try:
                raw.close()
            except Exception:
                pass
        gc.collect()


def ota_prepare_with_local_key():
    src = None
    dst = None
    replaced = False
    try:
        try:
            os.remove(OTA_READY_FILE)
        except Exception:
            pass
        src = open(OTA_RAW_FILE, "r")
        dst = open(OTA_READY_FILE, "w")
        for line in src:
            if line.startswith("OPENAI_API_KEY ="):
                dst.write("OPENAI_API_KEY = " + repr(OPENAI_API_KEY.strip()) + "\n")
                replaced = True
            else:
                dst.write(line)
        try:
            dst.flush()
        except Exception:
            pass
        src.close()
        src = None
        dst.close()
        dst = None
        if not replaced:
            return False, "API ANAHTAR SATIRI BULUNAMADI"
        return True, None
    except Exception as exc:
        return False, "DOSYA HAZIRLAMA: " + str(exc)
    finally:
        if src is not None:
            try:
                src.close()
            except Exception:
                pass
        if dst is not None:
            try:
                dst.close()
            except Exception:
                pass
        try:
            os.remove(OTA_RAW_FILE)
        except Exception:
            pass


def ota_install_ready():
    if not safe_write_text(OTA_STATE_FILE, "installing\n"):
        return False, "OTA DURUMU YAZILAMADI"
    try:
        try:
            os.remove(OTA_BACKUP_FILE)
        except Exception:
            pass
        os.rename("main.py", OTA_BACKUP_FILE)
        try:
            os.rename(OTA_READY_FILE, "main.py")
        except Exception:
            os.rename(OTA_BACKUP_FILE, "main.py")
            raise
        if not safe_write_text(OTA_STATE_FILE, "trial\n"):
            try:
                os.remove("main.py")
            except Exception:
                pass
            os.rename(OTA_BACKUP_FILE, "main.py")
            raise OSError("deneme durumu yazilamadi")
        return True, None
    except Exception as exc:
        try:
            os.remove(OTA_STATE_FILE)
        except Exception:
            pass
        return False, "KURULUM HATASI: " + str(exc)


def ota_confirm_boot():
    try:
        f = open(OTA_STATE_FILE)
        state = f.read().strip()
        f.close()
    except Exception:
        return
    if state == "trial":
        for path in (OTA_STATE_FILE, OTA_BACKUP_FILE, OTA_RAW_FILE):
            try:
                os.remove(path)
            except Exception:
                pass


def ota_restore_trial():
    try:
        f = open(OTA_STATE_FILE)
        state = f.read().strip()
        f.close()
    except Exception:
        return False
    if state != "trial":
        return False
    try:
        os.stat(OTA_BACKUP_FILE)
    except Exception:
        return False
    try:
        os.remove("main.py")
    except Exception:
        pass
    try:
        os.rename(OTA_BACKUP_FILE, "main.py")
    except Exception:
        return False
    try:
        os.remove(OTA_STATE_FILE)
    except Exception:
        pass
    return True


def openai_chat(messages, model, web_search, timeout, max_tok=None,
                reasoning=None, search_context="low"):
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
    endpoint = "/v1/responses"
    payload = json.dumps(body)
    transient_status = (0, 408, 429, 500, 502, 503, 504)
    last_error = "BAGLANTI HATASI"
    for attempt in range(GPT_RETRY_COUNT + 1):
        gc.collect()
        status = 0
        text = ""
        limit_reached = False
        empty_answer = False
        try:
            status, text = https_post("api.openai.com", endpoint,
                                       api_key, payload, timeout)
        except Exception as exc:
            last_error = "BAGLANTI HATASI: " + str(exc)
        finally:
            gc.collect()

        data = None
        if text:
            try:
                data = json.loads(text)
                text = None
                gc.collect()
            except Exception:
                last_error = "CEVAP COZULEMEDI"
        else:
            last_error = "BOS CEVAP GELDI"

        if status == 200 and data is not None:
            try:
                output_text = []
                for item in data.get("output", []):
                    if item.get("type") != "message":
                        continue
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            output_text.append(content.get("text", ""))
                if output_text:
                    return "\n".join(output_text), None
                incomplete = data.get("incomplete_details") or {}
                if incomplete.get("reason") == "max_output_tokens":
                    last_error = "GPT YANIT SINIRINA ULASTI"
                    limit_reached = True
                else:
                    last_error = "GPT BOS YANIT VERDI"
                    empty_answer = True
            except Exception:
                last_error = "BEKLENMEYEN BICIM"
        elif status in transient_status and status != 0:
            last_error = "API GECICI HATA " + str(status)
        elif status not in transient_status and data is not None:
            try:
                return None, "API HATASI: " + data["error"]["message"]
            except Exception:
                return None, "API HATASI KOD " + str(status)

        if attempt < GPT_RETRY_COUNT:
            if limit_reached or empty_answer:
                body["max_output_tokens"] = (
                    WEB_RETRY_TOKENS if web_search else GPT_RETRY_OUTPUT_BUDGET)
                payload = json.dumps(body)
            time.sleep_ms(GPT_RETRY_DELAY_MS)

    return None, last_error


WEB_QUERY_HINTS = (
    "bugun", "yarin", "dun", "guncel", "son dakika", "su an", "simdi",
    "bu hafta", "bu ay", "bu yil", "en son", "hava", "yagmur",
    "sicaklik", "sogukluk", "nem", "ruzgar", "basinc", "uv", "gorus",
    "dolar", "euro", "avro", "altin", "gumus", "kur", "borsa",
    "hisse", "bitcoin", "btc", "ethereum", "eth", "kripto", "fiyat", "kac tl", "ne kadar",
    "haber", "haberler", "mac", "maclar", "skor", "skorlar",
    "puan durumu", "lig", "ligler", "fikstur", "fiksturler",
    "deprem", "depremler",
    "trafik", "kim kazandi", "secim", "internetten", "webden", "ara",
    "kontrol et",
)

SPORTS_QUERY_HINTS = (
    "mac", "maclar", "skor", "skorlar", "puan durumu",
    "lig", "ligler", "fikstur", "fiksturler",
)

_fast_live_q = ""
_fast_live_answer = ""
_fast_live_at = 0


def _normalize_question(q):
    text = str(q).lower()
    for src, dst in (
            ("ı", "i"), ("ş", "s"), ("ğ", "g"),
            ("ü", "u"), ("ö", "o"), ("ç", "c")):
        text = text.replace(src, dst)
    for separator in ".,?!:;()[]{}-/\\'\"":
        text = text.replace(separator, " ")
    return " " + " ".join(text.split()) + " "


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
    global _fast_live_q, _fast_live_answer, _fast_live_at
    text = _normalize_question(q)
    now = time.ticks_ms()
    if (text == _fast_live_q and _fast_live_answer and
            time.ticks_diff(now, _fast_live_at) < 60000):
        return _fast_live_answer
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
    if answer:
        _fast_live_q = text
        _fast_live_answer = answer
        _fast_live_at = now
    return answer


def ask_question(q, web_search=None, search_context="low"):
    if web_search is None:
        web_search = question_needs_web(q)
    if web_search:
        sp = WEB_SYSTEM_PROMPT % _today_text()
        tok = WEB_MAX_TOKENS
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
        reasoning="none" if web_search else "minimal",
        search_context=search_context)


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
    region = data.get("region")          # il (IP tabanli tespitte sehir/ilceden daha guvenilir)
    cc = data.get("country_code")
    cname = data.get("country_name")
    lat = data.get("latitude")
    lon = data.get("longitude")
    if not region or not cc:
        return None
    return region, cc, cname, lat, lon


def _geo_try_ipwho():
    # ipapi.co bazen bot korumasi/oran siniri yuzunden cevap vermeyebilir;
    # bu durumda yedek olarak ipwho.is denenir.
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
    # WiFi'a baglaninca IP uzerinden IL (bolge), ulke ve enlem/boylam
    # tespit edilir; SOR cevaplari (hava, kur vb.), namaz vakitleri ve
    # gun batimina gore otomatik isik kisma buna gore ayarlanir. Ekranda
    # gosterilmez, sadece arka planda kullanilir. Ilce/sehir duzeyi IP
    # tabanli tespitte sik yanlis cikabildigi icin sadece il (region)
    # kullanilir.
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
DIM_AT_MIN = -1          # gun batimi+30dk, gece yarisindan itibaren dakika (-1=bilinmiyor)
BRIGHTEN_AT_MIN = -1     # gun dogumu-30dk, gece yarisindan itibaren dakika (-1=bilinmiyor)
_sunset_day_key = ""     # DIM_AT_MIN/BRIGHTEN_AT_MIN'in hangi gun icin hesaplandigi
_dimmed_today = False    # bugun otomatik kisma zaten uygulandi mi
_brightened_today = False  # bugun otomatik fullestirme zaten uygulandi mi


def _parse_hm(s):
    # "18:26:27" -> (saat, dakika)
    parts = s.strip().split(":")
    return int(parts[0]), int(parts[1])


def sunset_sync():
    # Konumun (enlem/boylam) gun dogumu/batimi saatlerini internetten alir;
    # batisi DIM_AFTER_SUNSET_MIN dakika ileri kaydirip DIM_AT_MIN'e,
    # dogusu BRIGHTEN_BEFORE_SUNRISE_MIN dakika geri kaydirip
    # BRIGHTEN_AT_MIN'e yazar.
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
    # Basit URL encode; burada sehir/ulke isimleri ASCII tutuluyor.
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
    # Bugunun namaz vakitlerini internetten alir. Internet yoksa sessizce cikilir.
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
    # "2026-06-20T05:31" -> "05:31"
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



def _ask_and_show(q):
    # Guncel sorularda web arar, digerlerini dogrudan GPT'ye sorar.
    release_answer_buffers()
    gc.collect()
    use_web = question_needs_web(q)
    draw_answer_frame()
    answer = fast_live_answer(q) if use_web else None
    if answer is None:
        _gpt_wait_start()
        answer, err = ask_question(q, use_web)
    else:
        err = None
    if use_web and (err is not None or _answer_refuses_current(answer)):
        answer, err = ask_question(q, True, "medium")
    if use_web and (err is not None or _answer_refuses_current(answer)):
        fallback_q = (q + " Canli veri yoksa en son bildigin bilgiyi ve "
                      "bilginin tarihini belirterek dogrudan cevapla.")
        answer, err = ask_question(fallback_q, False)
    _gpt_wait_stop()
    apply_ans_size(ans_size_idx)
    if err is not None:
        txt = to_screen_text(err)
    else:
        txt = to_screen_text(strip_urls(answer))
    lines = wrap_full(txt, ANS_CHARS)
    if not lines:
        lines = [""]
    return show_answer(lines)


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


def _gpt_wait_step(force=False):
    global _gpt_wait_phase, _gpt_wait_last
    if not _gpt_wait_active or lcd is None:
        return
    now = time.ticks_ms()
    if not force and time.ticks_diff(now, _gpt_wait_last) < 90:
        return
    _gpt_wait_last = now
    for i in range(4):
        x = 10 + i * 10
        lcd.fill_rect(x - 1, 8, 8, 30, BG)
        h = _GPT_WAIT_HEIGHTS[(_gpt_wait_phase + i) % 4]
        y = 23 - h // 2
        _draw_round_rect(x, y, 6, h, 3, TITLE_COL)
    _gpt_wait_phase = (_gpt_wait_phase + 1) % 4


def _gpt_wait_start():
    global _gpt_wait_active, _gpt_wait_phase, _gpt_wait_last
    _gpt_wait_active = True
    _gpt_wait_phase = 0
    _gpt_wait_last = 0
    lcd.fill_rect(6, 6, 48, 34, BG)
    _gpt_wait_step(True)


def _gpt_wait_stop():
    global _gpt_wait_active
    _gpt_wait_active = False
    if lcd is not None:
        lcd.fill_rect(6, 6, 48, 34, BG)


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
        # Butonlar arasinda bosluk yok (bitisik); acik modda hepsi siyah
        # zeminli, koyu modda eskisi gibi farkli renkler.
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
        ntptime.settime()                       # RTC = UTC
        secs = time.time() + TZ_OFFSET * 3600
        tm = time.localtime(secs)
        rtc.datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))
        ntp_ok = True
        last_ntp = time.ticks_ms()
        return True
    except Exception:
        return False


def wifi_connect(ssid, pw, timeout=12000):
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
                time.sleep_ms(250)
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
    # Alt menu saatin yerlesimini degistirmez. Boylece menu acilip kapanirken
    # sadece alt serit yenilenebilir.
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


def _text_thick(txt, x, y, color, size=1, thick=0):
    # 5x7 fontu buyutmeden/buyuterek biraz kalinlastirir.
    lcd.text(txt, x, y, color, size)
    step = 1
    if thick >= 1:
        lcd.text(txt, x + step, y, color, size)
    if thick >= 2:
        lcd.text(txt, x, y + step, color, size)


def _prayer_draw_size(txt):
    # BUYUK modunda HEPSI satiri sigmazsa otomatik normal boyuta duser.
    size = 2 if prayer_size_idx == 1 else 1
    if prayer_mode_idx == 2 and len(txt) * 6 * size > WIDTH:
        size = 1
    return size


# Ust cubukta OTA sag kosede; MANUEL yalnizca cevrimdisiyken onun solunda.
OTA_TOP_TXT = "OTA"
OTA_TOP_W = len(OTA_TOP_TXT) * 6
OTA_TOP_X = WIDTH - OTA_TOP_W - 4
OTA_TOP_HIT_X0 = OTA_TOP_X - 10
TOPBTN_TXT = "MANUEL"
TOPBTN_W = len(TOPBTN_TXT) * 6
TOPBTN_X = OTA_TOP_X - TOPBTN_W - 12
TOPBTN_HIT_X0 = TOPBTN_X - 10          # dokunma alani biraz genis tutulur


def draw_status():
    # Ust durum satiri: solda baglanti durumu (dokununca her zaman wifi
    # ekrani acilir), sagda MANUEL (her zaman gorunur, elle saat ayari).
    # Konum ekranda gosterilmez; sadece SOR cevaplari/namaz vakitleri icin
    # arka planda IP'den tespit edilir (bkz. geo_locate()).
    lcd.fill_rect(0, 0, WIDTH, 18, BG)
    online = is_online()
    lcd.text(OTA_TOP_TXT, OTA_TOP_X, 3, GREEN if online else GRAY, 1)
    if online:
        return
    lt = time.localtime()
    if ntp_ok:
        lcd.text("NTP", 4, 3, GREEN, 1)
    elif WIFI_SSID:
        lcd.text("WIFI?", 4, 3, AMBER, 1)
    else:
        lcd.text("AYAR'DAN KUR", 4, 3, GRAY, 1)

    if not USE_24H:
        ap = "OO" if lt[3] < 12 else "OS"
        lcd.text(ap, TOPBTN_X - 18, 3, GRAY, 1)
    lcd.text(TOPBTN_TXT, TOPBTN_X, 3, FG, 1)


def draw_bottom():
    lcd.fill_rect(0, BTN_Y, WIDTH, BTN_H, BG)
    # Alt menu her zaman gorunur.
    lcd.hline(0, BTN_Y, WIDTH, GRAY)
    labels = ("AYARLAR", MODE_NAMES[mode_idx], "GPT")
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
# Ortada saniyesiz dijital saat (HH:MM, ornek 08:50).
# Etrafinda 30 ESIT uzunlukta cizgi. Her cizgi 2 saniye = 1 cizgi.
# Cizgiler saniye gectikce gri -> beyaz dolar. Yeni dakikada sifirlanir.
# ============================================================
AN_CX = 160
AN_CY = 102          # cizgi halkasi yukarida
AN_R = 90            # cizgi halkasinin dis yaricapi (kalin cizgiye gore genis)
AN_TICKS = 60        # toplam cizgi sayisi (her saniye 1 cizgi)
AN_TICK_LEN = 16     # her cizginin uzunlugu (biraz daha uzun, hepsi esit)
_PI = 3.14159265

_an_last_fill = -1
_an_last_min = -1
_an_date_prev = ""
_an_prayer_prev = ""

# Analog ekranda namaz paneli (halkanin solundaki bos alan).
# Halka sol kenari x=70 civari; panel x 2..68 arasinda kalir.
AN_PR_X = 2
AN_PR_Y = 22
AN_PR_W = 66
AN_PR_H = 166


def _an_tick_geom(i):
    # i. cizginin ic ve dis koordinatlari (hepsi esit uzunlukta).
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
    # Cizgiyi kalin (2 px) ciz: ana cizgi + radyal yone dik 1 px kaydirma.
    # Boylece her modda net gorunur.
    x0, y0, x1, y1 = _an_tick_geom(i)
    lcd.line(x0, y0, x1, y1, color)
    a = i * (2.0 * _PI / AN_TICKS)
    ox = 1 if math.cos(a) >= 0 else -1     # radyal yone yaklasik dik kaydirma
    oy = 1 if math.sin(a) >= 0 else -1
    lcd.line(x0 + ox, y0, x1 + ox, y1, color)
    lcd.line(x0, y0 + oy, x1, y1 + oy, color)


def analog_tick_ring(filled):
    # Cizgileri cizer: dolmus (gecmis) saniyeler RING_FULL, dolmamislar
    # RING_EMPTY. Renkler moda gore net kontrast verir -> ilerleme belli.
    for i in range(AN_TICKS):
        _an_draw_tick(i, RING_FULL if i < filled else RING_EMPTY)


def _an_fill_from_sec(sec):
    # 60 saniye -> 60 cizgi. Her saniye 1 cizgi dolar.
    if sec > AN_TICKS:
        sec = AN_TICKS
    return sec


def _analog_prayer_key(lt):
    # Paneli sadece gerekince yeniden cizmek icin sade durum anahtari.
    return (_prayer_display_text(lt) + "|" + str(prayer_mode_idx) + "|" +
            str(prayer_thick_idx) + "|" + str(prayer_gap_idx) + "|" + str(mode_idx))


def analog_prayer_panel(lt, force=False):
    # Namaz vakitleri analog ekranda solda alt alta. Panel dar oldugu icin
    # yazi boyutu her zaman 1.
    global _an_prayer_prev
    key = _analog_prayer_key(lt)
    if not force and key == _an_prayer_prev:
        return
    _an_prayer_prev = key
    lcd.fill_rect(AN_PR_X, AN_PR_Y, AN_PR_W, AN_PR_H, BG)
    if prayer_mode_idx == 0:
        return
    head = FG
    val = FG

    if not prayer_text:
        # Vakit henuz yoksa namaz acik oldugunu yine de goster.
        lcd.text("NAMAZ", AN_PR_X + 4, AN_PR_Y + 12, head, 1)
        if is_online():
            lcd.text("ALINIYOR", AN_PR_X + 2, AN_PR_Y + 28, GRAY, 1)
        elif WIFI_SSID:
            lcd.text("WIFI?", AN_PR_X + 6, AN_PR_Y + 28, GRAY, 1)
        else:
            lcd.text("WIFI", AN_PR_X + 8, AN_PR_Y + 28, GRAY, 1)
            lcd.text("YOK", AN_PR_X + 10, AN_PR_Y + 42, GRAY, 1)
        return

    if prayer_mode_idx == 1:
        # En yakin vakit: ad ustte, saat altta.
        near = _nearest_prayer_text(lt)          # ORN: "OG 13:10"
        parts = near.split(" ")
        name = parts[0] if parts else "--"
        tm = parts[1] if len(parts) > 1 else "--:--"
        lcd.text("YAKIN", AN_PR_X + 4, AN_PR_Y + 10, head, 1)
        _text_thick(name, AN_PR_X + 6, AN_PR_Y + 30, val, 1, prayer_thick_idx)
        _text_thick(tm, AN_PR_X + 6, AN_PR_Y + 48, val, 1, prayer_thick_idx)
        return

    # HEPSI modu: tum vakitler alt alta.
    lcd.text("NAMAZ", AN_PR_X + 4, AN_PR_Y + 2, head, 1)
    y = AN_PR_Y + 18
    line_h = 14 + prayer_gap_idx * 3
    for name, tm in prayer_times:
        if y > AN_PR_Y + AN_PR_H - 12:
            break
        _text_thick(name + " " + tm, AN_PR_X + 4, y, val, 1, prayer_thick_idx)
        y += line_h


def analog_center_time(lt, force=False):
    # Ortada saniyesiz buyuk dijital saat (HH:MM). Tam ortalanmis.
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
    adv = 6 * size          # bir karakterin tam genisligi (bosluk dahil)
    char_w = 5 * size       # gercek piksel genisligi (son bosluk haric)
    th = 7 * size
    # Yatay: son karakterin bosluğunu saymadan tam ortala.
    tw = (len(s) - 1) * adv + char_w
    startx = AN_CX - tw // 2
    starty = AN_CY - th // 2

    # Sadece yazi alanini temizle (cizgilere dokunma).
    lcd.fill_rect(startx - 4, starty - 4, tw + 8, th + 8, BG)
    for i, ch in enumerate(s):
        lcd.text(ch, startx + i * adv, starty, col, size)


def analog_center_date(lt, force=False):
    # Cizgi halkasinin altinda gun + tarih.
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
    # Dolan cizgi kadar beyaz, kalani gri.
    analog_tick_ring(fill)
    # Ortada dijital saat.
    analog_center_time(lt, True)
    # Altta tarih.
    analog_center_date(lt, True)
    # Solda namaz vakitleri.
    analog_prayer_panel(lt, True)


def analog_update(lt, day_changed):
    global _an_last_fill
    fill = _an_fill_from_sec(lt[5])
    if fill != _an_last_fill:
        if fill < _an_last_fill:
            # Yeni dakika: tum cizgileri gri yap (sifirla).
            analog_tick_ring(fill)
        else:
            # Yeni dolan cizgileri dolu rengine boya.
            for i in range(_an_last_fill, fill):
                _an_draw_tick(i, RING_FULL)
        _an_last_fill = fill

    # Saat dakikasi degisince ortadaki yazi guncellenir.
    analog_center_time(lt)
    # Namaz paneli (sadece degisince yeniden cizilir).
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
# Ortada buyuk dijital HH:MM. Saat tek haneliyse (12 saat bicimi,
# 1-9 arasi) yaninda gizli bir "0" varmis gibi davranilmaz; yazi
# oldugu gercek genislige gore HER SEFERINDE yeniden ortalanir.
# Iki yaninda 5'er cubuktan olusan birer sutun; her saniye basinda
# merkezden disariya dogru bir NABIZ DALGASI yayilir (EKG/ekolayzer
# gibi cubuklar sirayla yukselip iner). Analog degil, tamamen
# dijital ve hareketli.
# ============================================================
PULSE_SIZE = 5
PULSE_Y = 90
_padv = PULSE_SIZE * 6
_ptw_max = 4 * _padv + 5 * PULSE_SIZE   # en genis olasi yazi ("12:45", 5 karakter)

BAR_W2 = 8
BAR_STEP = 13
BAR_BUFFER = 10                          # yazi ile cubuklar arasindaki bosluk
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
    # Tek haneli saat (12 saat bicimi) "0" ile doldurulmaz; boylece
    # metnin gercek genisligi degisir ve ona gore ortalanir.
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
            continue    # ":" ayri fonksiyonla (nabiz) cizilir
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
    # tier 0 = merkeze en yakin cubuk (once o yukselir), disariya dogru gecikmeli
    delay = tier * 0.15
    lp = frac - delay
    if lp < 0.0 or lp > 0.4:
        return BAR_BASE_H
    x = lp / 0.4
    shape = 1.0 - abs(1.0 - 2.0 * x)     # ucgen nabiz: 0 -> 1 -> 0
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
    # color'u BG'ye dogru soldurur (num/den orani parlaklik, 0=BG, den=tam renk).
    # Boylece koyu modda siyaha, acik modda beyaza dogru dogru sonmus olur.
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
    # level 0..6 -> iki noktanin parlakligi (nabiz)
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
    # frac_total: 0..1 (dakika icindeki oran) -> akici dolan cubuk
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
    # buyuk yazi modelinde iki ":" hucresini nabiz gibi soldur
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
    # ucgen nabiz: ortada parlak (6), uclarda sonuk
    t = frac * 2.0
    if t > 1.0:
        t = 2.0 - t
    lv = int(2 + t * 4)        # 2..6
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
    # saniye icinde akan animasyon (anim_on iken cagirilir)
    if face_idx == 1:
        # Analogda cizgiler saniye basi guncelleniyor; ara animasyon yok.
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
    # model degisirken hizli yatay silme efekti
    if not anim_on:
        return
    step = 12
    for x in range(0, WIDTH, step):
        lcd.fill_rect(x, 16, step, BTN_Y - 16, BG)
        time.sleep_ms(3)


# ---- HAVA ANIMASYONU: KAR / YAGMUR ----
# Sadece BUYUK YAZI (face_idx==2) ekraninda calisir.
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
        return 0      # kar
    return 1          # yagmur


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
    # Sadece bir satirin degerini yeniler (+/- basinca ekran komple
    # yenilenmesin diye).
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
    data = "%d %d %d %d %d %d %d %d %d %d %d %d %d\n" % (
        mode_idx, face_idx, bright_idx,
        1 if screen_flip else 0,
        1 if USE_24H else 0,
        ans_size_idx, ans_len_idx,
        weather_idx, prayer_mode_idx,
        prayer_size_idx,
        prayer_thick_idx,
        prayer_gap_idx,
        bright_value)
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
            mode_idx = int(p[0]) % len(MODE_NAMES)
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
            prayer_size_idx = int(p[9]) % len(PRAYER_SIZE_NAMES)
        if len(p) >= 11:
            prayer_thick_idx = int(p[10]) % len(PRAYER_THICK_NAMES)
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
    prayer_values = [
        ("MOD", PRAYER_MODE_NAMES[prayer_mode_idx], True),
        ("BOYUT", PRAYER_SIZE_NAMES[prayer_size_idx], True),
        ("KALIN", PRAYER_THICK_NAMES[prayer_thick_idx], True),
    ]
    prayer_y = (52, 110, 168)
    for i, (label, value, enabled) in enumerate(prayer_values):
        if i:
            lcd.hline(_SET_COL_W, prayer_y[i] - 14, _SET_COL_W, DARKGRAY)
        _settings_col_text(1, label, prayer_y[i], GRAY)
        _settings_col_text(1, value, prayer_y[i] + 21, FG if enabled else GRAY)


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
    device_x = ex - 32
    device_y = 91 if preview_flip else 72
    device_w = 65
    device_h = 49
    port_x = ex + 12 if preview_flip else ex - 12
    lcd.rect(device_x, device_y, device_w, device_h, FG)
    lcd.rect(device_x + 4, device_y + 4, device_w - 8, device_h - 8, GRAY)
    if preview_flip:
        # Fotograftaki gibi: port ustte, dirsekli fis sola dogru cikiyor.
        lcd.fill_rect(port_x - 5, device_y - 3, 11, 4, TITLE_COL)
        lcd.fill_rect(port_x - 8, device_y - 13, 17, 11, DARKGRAY)
        lcd.rect(port_x - 8, device_y - 13, 17, 11, FG)
        lcd.fill_rect(3 * _SET_COL_W + 1, device_y - 10,
                      port_x - 8 - (3 * _SET_COL_W + 1), 5, GRAY)
        lcd.hline(3 * _SET_COL_W + 1, device_y - 11,
                  port_x - 8 - (3 * _SET_COL_W + 1), FG)
    else:
        # 180 derece cevrilince ayni fiziksel giris alta, kablo saga gelir.
        port_y = device_y + device_h - 1
        lcd.fill_rect(port_x - 5, port_y, 11, 4, TITLE_COL)
        lcd.fill_rect(port_x - 8, port_y + 3, 17, 11, DARKGRAY)
        lcd.rect(port_x - 8, port_y + 3, 17, 11, FG)
        lcd.fill_rect(port_x + 9, port_y + 6,
                      3 * _SET_COL_W + _SET_COL_W - (port_x + 9), 5, GRAY)
        lcd.hline(port_x + 9, port_y + 5,
                  3 * _SET_COL_W + _SET_COL_W - (port_x + 9), FG)
    _settings_col_text(3, direction, 180, FG)


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
    global prayer_mode_idx, prayer_size_idx, prayer_thick_idx, prayer_gap_idx
    global ans_size_idx, ans_len_idx

    if col == 0:
        if y < 123:
            ans_size_idx = (ans_size_idx + 1) % len(SIZE_PROFILES)
            apply_ans_size(ans_size_idx)
        else:
            ans_len_idx = (ans_len_idx + 1) % len(LEN_PROFILES)
    elif col == 1:
        zone = (y - 38) // 59
        if zone <= 0:
            prayer_mode_idx = (prayer_mode_idx + 1) % len(PRAYER_MODE_NAMES)
        elif zone == 1:
            prayer_size_idx = (prayer_size_idx + 1) % len(PRAYER_SIZE_NAMES)
        else:
            prayer_thick_idx = (prayer_thick_idx + 1) % len(PRAYER_THICK_NAMES)
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


def _ota_confirm_screen(version, notes):
    lcd.fill(BG)
    lcd.text("YAZILIM GUNCELLEMESI", 34, 14, TITLE_COL, 2)
    incoming = "SURUM  v" + version
    lcd.text(incoming, (WIDTH - len(incoming) * 6) // 2, 51, GREEN, 1)
    lcd.hline(24, 72, WIDTH - 48, DARKGRAY)
    lcd.text("YENILIKLER", 127, 84, TITLE_COL, 1)
    shown_notes = notes if notes else ["Genel iyilestirmeler"]
    y = 106
    for note in shown_notes[:4]:
        line = "- " + to_screen_text(note)
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


def run_ota_update():
    if not is_online():
        show_status_screen("OTA ICIN WIFI GEREKLI", AMBER)
        time.sleep_ms(1400)
        return
    show_status_screen("GUNCELLEME KONTROL EDILIYOR", TITLE_COL)
    release_answer_buffers()
    gc.collect()
    manifest, err = ota_check_manifest()
    if err is not None:
        show_status_screen(to_screen_text(err)[:48], RED)
        time.sleep_ms(1800)
        return
    if _ota_version_parts(manifest["version"]) <= _ota_version_parts(APP_VERSION):
        show_status_screen("SURUM GUNCEL: v" + APP_VERSION, GREEN)
        time.sleep_ms(1400)
        return
    if not _ota_confirm_screen(manifest["version"], manifest.get("notes", [])):
        return

    download_url = manifest["url"]
    expected_sha = manifest["sha256"]
    manifest = None
    release_answer_buffers()
    gc.collect()

    lcd.fill(BG)
    lcd.text("YAZILIM GUNCELLENIYOR", 28, 76, TITLE_COL, 2)
    _ota_draw_progress(0, 1)
    ok, err = ota_download(download_url, expected_sha)
    if not ok:
        show_status_screen(to_screen_text(err)[:48], RED)
        time.sleep_ms(2200)
        return
    download_url = None
    expected_sha = None
    gc.collect()
    show_status_screen("API ANAHTARI KORUNUYOR", TITLE_COL)
    ok, err = ota_prepare_with_local_key()
    if not ok:
        show_status_screen(to_screen_text(err)[:48], RED)
        time.sleep_ms(2200)
        return
    gc.collect()
    show_status_screen("DOGRULANDI, KURULUYOR", GREEN)
    ok, err = ota_install_ready()
    if not ok:
        show_status_screen(to_screen_text(err)[:48], RED)
        time.sleep_ms(2200)
        return
    show_status_screen("TAMAM, YENIDEN BASLIYOR", GREEN)
    time.sleep_ms(1200)
    if machine_reset is not None:
        machine_reset()
    while True:
        time.sleep_ms(1000)


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
        if y < 38:
            _wait_touch_release()
            continue
        col = min(3, x // _SET_COL_W)
        if col == 2:
            dragging_brightness = True
            _settings_set_brightness(y)
            continue
        _wait_touch_release()
        if col == 3:
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
    # Kose yaricapli dikdortgen. Kenarlik, dolguyla AYNI satir-bazli
    # hesabi kullanarak tek piksel olarak cizilir; boylece dolgu ile
    # kenarlik birebir orusur (ayri bir daireyle ic ice cizmenin
    # kose ucunda birakti kalinlasma/yigilma hatasi olmaz).
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
    # Aktif: on plan renginde (moda gore parlak) dolgu + zemin rengi yazi.
    # Pasif: her modda okunur olsun diye sabit koyu gri + beyaz yazi.
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
_PRAYER_SIZE_Y = 132
_PRAYER_THICK_Y = 160
_PRAYER_GAP_Y = 188


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
    _draw_prayer_option_row(_PRAYER_THICK_Y, "KALINLIK", PRAYER_THICK_NAMES[prayer_thick_idx], True)
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
    if 22 <= x <= WIDTH - 22 and _PRAYER_THICK_Y <= y <= _PRAYER_THICK_Y + 24:
        return 4
    if 22 <= x <= WIDTH - 22 and _PRAYER_GAP_Y <= y <= _PRAYER_GAP_Y + 24:
        return 5
    if y >= 216:
        return 6
    return None


def _draw_prayer_slider_screen(title, value, count, mode):
    _panel_header(title)
    lcd.fill_rect(0, 48, WIDTH, 72, BG)
    col = FG
    if mode == "size":
        size = 2 if value == 1 else 1
        txt = "YAKIN IM 05:20"
        x = (WIDTH - len(txt) * 6 * size) // 2
        if x < 2:
            x = 2
        y = 70 if size == 1 else 62
        _text_thick(txt, x, y, col, size, prayer_thick_idx)
        hint = "Namaz yazisi boyutu icin kaydir"
    elif mode == "thick":
        txt = "YAKIN IM 05:20"
        size = 2 if prayer_size_idx == 1 else 1
        x = (WIDTH - len(txt) * 6 * size) // 2
        if x < 2:
            x = 2
        y = 70 if size == 1 else 62
        _text_thick(txt, x, y, col, size, value)
        hint = "Namaz yazisi kalinligi icin kaydir"
    else:
        gap = " " * (value + 1)
        txt = "IM 05:20" + gap + "OG 13:10" + gap + "IK 16:45" + gap + "AK 20:20"
        x = (WIDTH - len(txt) * 6) // 2
        if x < 2:
            x = 2
        _text_thick(txt, x, 78, col, 1, prayer_thick_idx)
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
    global prayer_mode_idx, prayer_size_idx, prayer_thick_idx, prayer_gap_idx
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
        if sel == 6:
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
        elif sel == 4:
            prayer_thick_idx = _run_prayer_slider("YAZI KALINLIGI", prayer_thick_idx,
                                                  len(PRAYER_THICK_NAMES), "thick")
            save_cfg()
            _prayer_menu_draw()
        elif sel == 5 and prayer_mode_idx == 2:
            prayer_gap_idx = _run_prayer_slider("BOSLUK", prayer_gap_idx,
                                                len(PRAYER_GAP_NAMES), "gap")
            save_cfg()
            _prayer_menu_draw()


# ---- DIGER AYARLAR PANELI ----
# 24 saat bicimi sabit; burada sadece ekran donme, namaz ve GPT cevap
# ayarlari kaldi.
_EBTN = [
    (80, 90, "DON"),
    (80, 170, "NAMAZ"),
    (240, 170, "SOR"),
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

    _draw_rotate_icon(80, 90, screen_flip)
    _draw_circle_button(80, 170, 24, "NM", prayer_mode_idx != 0, "NAMAZ")
    _draw_circle_button(240, 170, 24, "SOR", False, "GPT AYARI")

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
            run_prayer_settings()
            _extra_panel_draw()
        elif sel == 2:
            run_sor_settings()
            _extra_panel_draw()


# ---- SOR MENUSU: KLAVYE / HAZIR SORULAR ----
# Hazir sorular basit elips (pill) sekilleri icinde gosterilir. Pil
# uzerindeki yazi kisa kalsin diye (etiket, gercek soru) ciftleri
# tutulur: AI'ya etiketten daha detayli, tam bir soru gonderilir.
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

_SOR_PILL_Y0 = 44       # sekmelerin (36px) hemen altinda, 8px bosluk
_SOR_PILL_H = 26
_SOR_PILL_PAD = 10      # yazi ile pilin kenari arasi ic bosluk
_SOR_GAP_X = 8          # yan yana pillar arasi bosluk
_SOR_GAP_Y = 8          # satirlar arasi bosluk
_SOR_MARGIN_X = 10


def _half_ring(cx, cy, r, color, side):
    # Cemberin sadece disa bakan yarisini cizer (side<0 sol, side>0 sag).
    # Boylece pilin dis hatti tek parca gibi durur; ortadaki dikdortgenle
    # birlestigi yerde iki daireden yapildigini ele veren dikis olusmaz.
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
    # Elips/hap sekli: orta dikdortgen + iki ucta dolu yarim daire.
    # Dis hat (kenar cizgisi) her iki ucta sadece disa bakan yarim
    # cember olarak cizilir; ic dikis gorunmez.
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
    # Her soru kendi ETIKET genisligi kadar pil olur (AI'ya gidecek
    # tam soru daha uzun olabilir, pil boyutunu etkilemez). Yan yana
    # sigdikca yan yana dizilir; sigmayan (ya da satirda ilk soru
    # olan) tek basina yeni satira gecer. Sola yasli, simetri aranmaz.
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


# Ust cubukta sadece kucultulmus GPT/HAZIR SORU sekmeleri var.
# GERI butonu her ekranda kendi yerinde: HAZIR SORU'da eskisi gibi
# alttaki seritte; KLAVYE'de M/L harflerinin yanindaki bosluga,
# TAMAM'in tam ustune gelecek sekilde klavyenin icine gomulu.
_SOR_TABS_Y0 = 6
_SOR_TABS_H = 24
_SOR_CONTENT_Y0 = _SOR_TABS_Y0 + _SOR_TABS_H + 6   # icerigin basladigi satir


def _sor_tabs_draw(active):
    # Sekmeler yer degistirdi: solda HAZIR SORU, sagda GPT.
    # (Ic mantikta 0=GPT klavyesi 1=HAZIR SORU sabit kaldi, sadece fiziksel
    # yerlesim ters cevrildi.)
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
    # Sekme alanina dokunuldu mu? 0=KLAVYE 1=HAZIR SORU, degilse None.
    # Sol=HAZIR SORU(1), sag=KLAVYE(0) (fiziksel yerlesim ters).
    if y < _SOR_TABS_Y0 or y > _SOR_TABS_Y0 + _SOR_TABS_H:
        return None
    return 1 if x < WIDTH // 2 else 0


_SOR_HAZIR_GERI_Y = 214
_SOR_HAZIR_GERI_H = 26


def _sor_hazir_draw():
    lcd.fill_rect(0, 0, WIDTH, HEIGHT, BG)
    _sor_tabs_draw(1)
    for (x, y, w, h, label, question) in _sor_pill_layout():
        _draw_pill(x, y, w, h, DARKGRAY, GRAY, label, WHITE)
    lcd.fill_rect(0, _SOR_HAZIR_GERI_Y, WIDTH, _SOR_HAZIR_GERI_H, DARKGRAY)
    lcd.hline(0, _SOR_HAZIR_GERI_Y, WIDTH, GRAY)
    lcd.text("GERI", (WIDTH - 24) // 2, _SOR_HAZIR_GERI_Y + 9, WHITE, 1)


# ---- SOR: KLAVYE sekmesi (ust cubukta sadece sekmeler, GERI klavyede) ----
_SOR_IN_X = 4
_SOR_IN_Y = _SOR_CONTENT_Y0 + 2

# GERI tusu, 'm' harfinin saginda kalan bos alana, TAMAM'in tam
# ustune gelecek sekilde ek bir klavye tusu olarak yerlestirilir.
_SOR_KB_GERI_X = 272
_SOR_KB_GERI_Y = KB_TOP + 3 * (KEY_H + 2)
_SOR_KB_GERI_W = WIDTH - _SOR_KB_GERI_X


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
    # Normal klavye tuslarina ek olarak, 'm'nin yanindaki bos alana
    # gomulu bir GERI tusu ekler (TAMAM'in tam ustunde kalir).
    keys = _kb_build(mode)
    keys.append({"label": "GERI", "x": _SOR_KB_GERI_X, "y": _SOR_KB_GERI_Y,
                 "w": _SOR_KB_GERI_W, "h": KEY_H, "kind": "geri"})
    return keys


def _run_sor_keyboard():
    # Donus: yazilan soru metni, None (GERI ile SOR'dan tamamen cikildi,
    # ana ekrana donulur) ya da "__switch__" (HAZIR SORU'ya gecis istendi).
    text = ""
    mode = "low"
    keys = _sor_kb_build(mode)
    lcd.fill_rect(0, 0, WIDTH, HEIGHT, BG)
    _sor_tabs_draw(0)
    _kb_draw(keys)
    _sor_in_draw_all(text)
    last = 0
    while True:
        p = touch.read_fast()
        if p is None:
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
    # view: 0=KLAVYE 1=HAZIR SORU (varsayilan acilis)
    view = 1
    while True:
        if view == 0:
            q = _run_sor_keyboard()
            if q is None:
                return          # GERI (klavyede) -> ana ekrana don
            if q == "__switch__":
                view = 1
                continue
            q = q.strip()
            if q:
                act = _ask_and_show(q)
                if act == "back":
                    view = 1
                    continue
            continue        # "new" ya da bos soru -> klavye sekmesinde kal

        _sor_hazir_draw()
        _wait_touch_release()
        last = 0
        next_view = None
        while next_view is None:
            p = touch.read_fast()
            if p is None:
                time.sleep_ms(20)
                continue
            now = time.ticks_ms()
            if time.ticks_diff(now, last) < TOUCH_DEBOUNCE_MS:
                continue
            last = now
            x, y = p
            if y >= _SOR_HAZIR_GERI_Y:          # GERI (alttaki serit)
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


def open_sor():
    if is_online():
        run_sor()
    else:
        show_status_screen("ONCE WIFI BAGLAN", AMBER)
        time.sleep_ms(1200)
    draw_static()


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


def boot_anim():
    lcd.fill(BG)
    cx = WIDTH // 2
    cy = 92
    radius = 54
    title = "MASA SAATI"
    lcd.text(title, (WIDTH - len(title) * 12) // 2, 166, TITLE_COL, 2)
    subtitle = "PICO 2 W"
    lcd.text(subtitle, (WIDTH - len(subtitle) * 6) // 2, 194, GRAY, 1)

    # Kadran soldan saga tamamlanirken alttaki ince cizgi de ilerler.
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
    load_wifi()
    if WIFI_SSID and network is not None:
        wifi_reconnect_start(WIFI_SSID, WIFI_PASS)
    try:
        bl_pwm = PWM(Pin(LCD_BL))
        bl_pwm.freq(1000)
        bl_pwm.duty_u16(bright_value)
    except Exception:
        bl_pwm = None
    if screen_flip:
        lcd.set_rotation(True)

    if anim_on:
        boot_anim()
    else:
        boot_msg("MASA SAATI", TITLE_COL)
        time.sleep_ms(600)

    draw_static()
    ota_confirm_boot()

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
    last_gc = last_wifi_retry
    was_online = is_online()
    network_sync_stage = 0 if was_online else -1

    while True:
        now = time.ticks_ms()

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
                # Basili tutunca (her modelde, kar/yagmur dahil) saat degisir.
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
                    # Sag kosede OTA her zaman dokunulabilir. Cevrimdisiyken
                    # MANUEL onun solunda, WiFi ayari ise soldaki durumdadir.
                    if sx >= OTA_TOP_HIT_X0:
                        run_ota_update()
                        draw_static()
                    elif not is_online():
                        if sx >= TOPBTN_HIT_X0:
                            run_set()
                            draw_static()
                        else:
                            run_wifi_setup()
                            draw_static()
                elif abs(dx) < 22 and abs(dy) < 22 and sy < BTN_Y - 4 and face_idx == 2:
                    # Kar/yagmur (buyuk yazi) modelinde kisa dokunma hava
                    # tipini degistirir. Saatler arasi gecis sadece basili
                    # tutarak (uzun basma) yapilir.
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
                        mode_idx = (mode_idx + 1) % len(MODE_NAMES)
                        apply_mode()
                        save_cfg()
                        draw_static()
                    else:
                        open_sor()
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
                network_sync_stage += 1
                if network_sync_stage > 3:
                    network_sync_stage = -1
                draw_status()
            if (WIFI_SSID and not online and
                    time.ticks_diff(now, last_wifi_retry) >= WIFI_RETRY_MS):
                last_wifi_retry = now
                wifi_reconnect_start(WIFI_SSID, WIFI_PASS)
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
            was_online = online
            if (DIM_AT_MIN >= 0 and not _dimmed_today
                    and lt[3] * 60 + lt[4] >= DIM_AT_MIN):
                # Gun batimindan DIM_AFTER_SUNSET_MIN dakika sonra isigi
                # otomatik olarak en dusuk ayara getir (tek seferlik).
                _dimmed_today = True
                if bright_value != BRIGHT_LEVELS[-1]:
                    bright_idx = len(BRIGHT_LEVELS) - 1
                    bright_value = BRIGHT_LEVELS[bright_idx]
                    if bl_pwm is not None:
                        bl_pwm.duty_u16(bright_value)
                    save_cfg()
            if (BRIGHTEN_AT_MIN >= 0 and not _brightened_today
                    and lt[3] * 60 + lt[4] >= BRIGHTEN_AT_MIN):
                # Gun dogumundan BRIGHTEN_BEFORE_SUNRISE_MIN dakika once isigi
                # otomatik olarak en yuksek ayara getir (tek seferlik).
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
        ota_restore_trial()
        try:
            lcd.fill(BG)
            lcd.text("HATA - YENIDEN BASLIYOR", 82, 112, RED, 1)
        except Exception:
            pass
        time.sleep_ms(1800)
        if machine_reset is not None:
            machine_reset()
        raise


run_clock()
