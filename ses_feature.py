# Ses -> yazi. I2S mikrofondan kayit alir, OpenAI'ye yollar, gelen metni
# ekranda gosterir.
#
# DONANIM: I2S MEMS mikrofon (INMP441 sinifi).
#   SCK -> GP18, WS -> GP19, SD -> GP20, VDD -> 3V3, GND -> GND, L/R -> GND
# RP2'de WS pini SCK'nin bir fazlasi olmak ZORUNDA, pinler keyfi secilemez.
#
# NEDEN KAYIT RAM'E ALINIYOR: I2S calisirken flash'a yazmak cihazi sert
# resetliyor. Olculdu: I2S kurulumu, okuma ve I2S acikken tek bir dosya
# yazimi sorunsuz; ama kayit dongusunun icinde flash'a yazinca cihaz
# kilitleniyor ve USB'den bile dusuyor. Sebebi RP2'ye ozgu: flash yazimi
# sirasinda kod flash'tan calistirilamiyor, arka planda suren I2S DMA
# kesmesiyle cakisiyor. Bu yuzden ses once RAM'e toplanir, I2S KAPATILDIKTAN
# sonra dosyaya yazilir. Dosya yazilinca RAM tamponu birakilir; boylece TLS
# el sikismasi sirasinda 160 KB bosuna tutulmaz.

SCK_PIN = 18
WS_PIN = 19
SD_PIN = 20
ORNEK_HIZ = 16000
# Istenen ust sinir. Gercekte _tampon_ayir ne kadar yer bulabilirse o
# kadar kaydediliyor; cihazda olculdu, tavan ~7.4 saniye (232 KB).
# 8 yazmak "elde ne varsa hepsini kullan" demek.
KAYIT_SN = 8

# Modeller cihazin KENDI kaydiyla olculdu (4 sn, 3'er deneme):
#   gpt-4o-mini-transcribe  0.80 s  dogru      <- secildi
#   gpt-4o-transcribe       0.90 s  dogru      <- yedek
#   gpt-transcribe          0.88 s  BOS dondu
#   whisper-1               1.12 s  UYDURDU ("Altyazi M.K.")
# Yedek eskiden whisper-1'di; Mac'in temiz sentetik kaydinda dogru
# calisiyor ama gercek mikrofon kaydinda uyduruyor, o yuzden degistirildi.
# Sohbet modelleri (gpt-5.4-nano vb.) bu ucta calismaz, reddediliyor.
MODEL = "gpt-4o-mini-transcribe"
YEDEK_MODEL = "gpt-4o-transcribe"
DIL = "tr"

# Konusma bitince kendiliginden dur, bastaki sessizligi de gonderme.
# NEDEN: yuklenen veri suredeki en buyuk gecikme kalemi -- model tarafi
# 0.8 s, oysa 160 KB'i Pico'nun WiFi'sinden yollamak kat kat uzun suruyor.
# Sabit 5 saniye kaydedince 2 saniyelik cumle icin 3 saniye sessizlik de
# yukleniyordu. Ornek hizini dusurmek de yuku azaltirdi ama olculdu:
# 8 kHz'de model BOS donuyor, yani kaliteyi bozmadan kazanilacak yer burasi.
SES_ESIGI = 1500         # 16 bitlik olcek; sessizlik ~400, konusma 15000+
BITIS_SESSIZLIK_MS = 900
ON_PAY_MS = 250          # konusmanin basindan biraz once basla
# Basili tutma modunda parmagin kalktigina karar vermek icin gereken
# kesintisiz bosluk. Direncli dokunmatik ara ara bos okuyor.
BIRAKMA_MS = 200

_app = None

_REQUIRED = (
    "lcd", "touch", "time", "os", "gc", "json", "socket", "ssl",
    "OPENAI_API_KEY", "tls_connect", "log_error", "to_screen_text",
    "show_answer", "wrap_full", "_watchdog_touch", "_mini_saat_kose",
    "_wait_touch_release", "_buffer_find", "_dechunk", "_decode_buffer",
    "set_answer_header", "set_answer_text_color", "apply_ans_size",
    "release_answer_buffers", "SIZE_PROFILES", "ans_size_idx",
    "_gpt_wait_start", "_gpt_wait_stop", "_gpt_wait_step",
    "WIDTH", "HEIGHT", "BG", "FG", "GRAY", "DARKGRAY", "WHITE", "BLACK",
    "RED", "GREEN", "BLUE", "AMBER", "TITLE_COL",
)


def start(app):
    global _app
    _app = app
    here = globals()
    for name, value in app.__dict__.items():
        if name not in here:
            here[name] = value
    eksik = [n for n in _REQUIRED if n not in here]
    if eksik:
        raise RuntimeError("ses_feature eksik bagimlilik: " + ", ".join(eksik))
    return _run()


# ---- kayit ----

def _wav_basligi(veri_boyu):
    def u32(v):
        return bytes((v & 255, (v >> 8) & 255, (v >> 16) & 255, (v >> 24) & 255))

    def u16(v):
        return bytes((v & 255, (v >> 8) & 255))

    return (b"RIFF" + u32(36 + veri_boyu) + b"WAVEfmt " + u32(16) +
            u16(1) + u16(1) + u32(ORNEK_HIZ) + u32(ORNEK_HIZ * 2) +
            u16(2) + u16(16) + b"data" + u32(veri_boyu))


_CUBUK_X = 20
_CUBUK_Y = 118
_CUBUK_W = 280
_CUBUK_H = 26


def _seviye_ciz(oran, onceki):
    # Yalnizca degisen kisim boyanir: her blokta tum cubugu tazelemek
    # kaydin ritmini bozacak kadar surerdi.
    yeni = _CUBUK_W * oran // 100
    if yeni == onceki:
        return onceki
    if yeni > onceki:
        lcd.fill_rect(_CUBUK_X + onceki, _CUBUK_Y + 1, yeni - onceki,
                      _CUBUK_H - 2, GREEN)
    else:
        lcd.fill_rect(_CUBUK_X + yeni, _CUBUK_Y + 1, onceki - yeni,
                      _CUBUK_H - 2, BG)
    return yeni


def _kalan_ciz(kalan_ms):
    metin = "%d" % ((kalan_ms + 999) // 1000)
    lcd.fill_rect(WIDTH // 2 - 18, 160, 36, 24, BG)
    lcd.text(metin, WIDTH // 2 - 6 * len(metin), 162, TITLE_COL, 2)


BLOK_BOYU = 8192          # 4096 ornek, ~256 ms
I2S_TAMPON = 10000        # surucunun DMA tamponu, ~160 ms ses
BOS_TABAN = 60000         # yigina birakilacak asgari bos alan


def _tampon_ayir(hedef):
    """Kaydi TEK PARCA yerine bloklar halinde tutar ve yigini bosaltmaz.

    IKI DERS, ikisi de cihazda olculdu:
    1) Tek parca 160 KB istemek MemoryError veriyordu -- bos RAM yetiyor
       ama o kadar BITISIK alan kalmiyor. 8 KB'lik parcalar parcalanmis
       yigindan da bulunur.
    2) Bellek bitene kadar ayirmak da yanlisti: yigin kuruyunca sonraki
       islemler cokuyordu ('allocating 20000 bytes' hatasi I2S surucusunun
       kendi tamponundandi). Bu yuzden BOS_TABAN kadar alan hep birakilir.

    Yer darsa kayit kisalir; hic basarisiz olmaz.
    """
    bloklar = []
    kalan = hedef
    while kalan > 0:
        if gc.mem_free() < BOS_TABAN + BLOK_BOYU:
            break
        n = BLOK_BOYU if kalan > BLOK_BOYU else kalan
        try:
            bloklar.append(bytearray(n))
        except MemoryError:
            break
        kalan -= n
    return bloklar


def kaydet(basili=False):
    """Mikrofondan kayit alir. (bloklar, bas, son, tepe) doner.

    basili=True ise BASILI TUTULDUGU SURECE kaydeder ve parmak
    kalkinca durur. basili=False eski davranis: konusma bitince
    sessizlikten anlayip kendi durur.

    Ses RAM'de kalir; flash'a hic yazilmaz. Bu yuzden sure RAM ile
    sinirli: cihazda olculdu, 30 saniye 937 KB eder ama ancak 232 KB
    ayrilabiliyor -- tavan ~7 saniye.
    """
    from machine import I2S, Pin
    release_answer_buffers()
    gc.collect()
    ses = None
    bloklar = None
    p = 0
    tepe = 0
    try:
        # I2S ONCE kurulur. Surucu kendi DMA tamponu icin bitisik alan
        # istiyor; kayit bloklarini once ayirinca o alan kalmiyordu.
        ses = I2S(0, sck=Pin(SCK_PIN), ws=Pin(WS_PIN), sd=Pin(SD_PIN),
                  mode=I2S.RX, bits=32, format=I2S.MONO,
                  rate=ORNEK_HIZ, ibuf=I2S_TAMPON)
        bloklar = _tampon_ayir(ORNEK_HIZ * 2 * KAYIT_SN)
        hedef = 0
        for b in bloklar:
            hedef += len(b)
        if hedef < ORNEK_HIZ * 2:          # bir saniyeden az
            raise MemoryError("ses icin yer yok: bos=%d" % gc.mem_free())
        bi = 0
        blok = bloklar[0]
        blok_sinir = len(blok)
        bo = 0
        ham = bytearray(4096)
        # ACILIS GURULTUSU: I2S ilk acildiginda ~0.3 sn boyunca yuksek
        # genlikli cop uretiyor. Olculdu: kaydin ilk 0.3 saniyesinin RMS'i
        # 5358, kaydin genelinin RMS'i 1722 -- yani bas taraf konusmadan
        # bile gurultulu. Tek blok atmak yetmiyordu ve bu, konusma
        # algilamayi yaniltiyordu: gurultu "konusma basladi" sayilip
        # sessizlik sayaci hemen doluyor, kullanici konusmadan kayit
        # bitiyordu.
        # Ayni turda DC kaymasi da olculur: mikrofonun cikisi sifirda
        # degil, cihazda ortalama -349 olculdu (ayni cumlenin temiz
        # kaydinda -0.8). INMP441 sinifinin bilinen ozelligi; genligin
        # ~%1'ini bosa harciyor ve yeni transkripsiyon modelleri boyle
        # kayitlarda bos donuyor.
        atilacak = ORNEK_HIZ * 300 // 1000 * 4      # 300 ms ham veri
        while atilacak > 0:
            atilacak -= ses.readinto(ham)
        # DC ancak gurultu OTURDUKTAN SONRA olculebilir. Ilk denemede
        # olcumu atilan 300 ms'in icinde yapiyordum ve sonuc tam ters
        # etki yapti: DC -349'dan -3940'a cikti, cunku olcum gurultunun
        # kendisini olcuyordu. Simdi gurultu atildiktan sonraki 150 ms
        # kullaniliyor (o da kayda girmiyor).
        olcum = ORNEK_HIZ * 150 // 1000 * 4
        dc_top = 0
        dc_say = 0
        taban = 0
        while olcum > 0:
            n = ses.readinto(ham)
            olcum -= n
            for k in range(2, n, 16):              # her 8. ornek yeter
                v = (ham[k + 1] << 8) | ham[k]
                if v > 32767:
                    v -= 65536
                dc_top += v
                dc_say += 1
        dc = dc_top // dc_say if dc_say else 0
        # Ayni pencereden ortam gurultusunun tepesi de olculur.
        for k in range(2, n, 4):
            v = (ham[k + 1] << 8) | ham[k]
            if v > 32767:
                v -= 65536
            v -= dc
            if v < 0:
                v = -v
            if v > taban:
                taban = v
        # Konusma esigi ORTAMA gore: sabit esik sessiz odada calisip
        # gurultulu ortamda kaydi hemen kesiyordu (olculdu: ortam
        # tepesi 1589, sabit esik 1500 -> kayit 1.27 sn'de bitti).
        esik = taban * 3
        if esik < SES_ESIGI:
            esik = SES_ESIGI
        dc_acc = dc << 8
        lcd.fill_rect(_CUBUK_X, _CUBUK_Y, _CUBUK_W, _CUBUK_H, BG)
        lcd.rect(_CUBUK_X, _CUBUK_Y, _CUBUK_W, _CUBUK_H, GRAY)
        cubuk = 0
        son_kalan = -1
        # Geri sayim GERCEK kapasiteye gore: yer darsa kayit kisaliyor.
        sure_ms = hedef * 1000 // (ORNEK_HIZ * 2)
        bayt_ms = ORNEK_HIZ * 2 // 1000
        konusma = False
        sessiz_ms = 0
        birakma = 0
        bas = 0
        t0 = time.ticks_ms()
        while p < hedef:
            _watchdog_touch()
            n = ses.readinto(ham)
            gecen_blok_ms = (n >> 2) * 1000 // ORNEK_HIZ
            i = 2
            blok_tepe = 0
            while i < n and p < hedef:
                # DC BURADA cikariliyor, kayittan SONRA degil. Sonradan
                # ayri bir gecis yapmak olculdu: 5 saniyelik kayit icin
                # 1411 ms, yani kullanicinin bekledigi sureye eklenirdi.
                # Burada bedava: ornek basina 62 us butce var, dongu
                # bunun ancak kucuk bir kismini kullaniyor.
                v = (ham[i + 1] << 8) | ham[i]
                if v > 32767:
                    v -= 65536
                # Kendini ayarlayan DC takibi (tek kutuplu yuksek gecirgen,
                # ~10 Hz). Tek bir pencerede olcup sabit cikarmak kirilgan
                # cikti: olcum penceresi nereye dusuyorsa sonuc ona bagli
                # oluyordu (denendi, DC -349'dan once -3940'a sonra -791'e
                # gitti). Bu surum pencereden bagimsiz, kayma da izliyor.
                dc_acc += v - (dc_acc >> 8)
                v -= dc_acc >> 8
                if v > 32767:
                    v = 32767
                elif v < -32768:
                    v = -32768
                blok[bo] = v & 255
                blok[bo + 1] = (v >> 8) & 255
                bo += 2
                p += 2
                i += 4
                if v < 0:
                    v = -v
                if v > blok_tepe:
                    blok_tepe = v
                if bo >= blok_sinir:
                    bi += 1
                    if bi >= len(bloklar):
                        p = hedef
                        break
                    blok = bloklar[bi]
                    blok_sinir = len(blok)
                    bo = 0
            if blok_tepe > tepe:
                tepe = blok_tepe
            if blok_tepe >= esik:
                if not konusma:
                    konusma = True
                    bas = p - ON_PAY_MS * bayt_ms
                    if bas < 0:
                        bas = 0
                    bas -= bas % 2         # ornek sinirina hizala
                sessiz_ms = 0
            elif konusma and not basili:
                sessiz_ms += gecen_blok_ms
                if sessiz_ms >= BITIS_SESSIZLIK_MS:
                    break                  # konusma bitti
            cubuk = _seviye_ciz(min(100, blok_tepe // 230), cubuk)
            kalan = sure_ms - time.ticks_diff(time.ticks_ms(), t0)
            if kalan // 1000 != son_kalan:
                son_kalan = kalan // 1000
                _kalan_ciz(kalan if kalan > 0 else 0)
            if basili:
                # Parmak kalkinca dur. Direncli dokunmatik ara ara bos
                # okuyor, o yuzden tek bir bosluga degil UST USTE
                # BIRAKMA_MS kadar bosluga bakiliyor -- yoksa cumlenin
                # ortasinda kesilirdi.
                if touch.read_fast() is None:
                    birakma += gecen_blok_ms
                    if birakma >= BIRAKMA_MS:
                        break
                else:
                    birakma = 0
                # Basili tutarken bastaki sessizlik kirpilmasin: kullanici
                # tusa basip konusmaya baslayana kadar gecen sure zaten kisa.
                if not konusma:
                    bas = 0
            elif touch.read_fast() is not None:
                break                      # erken bitir
    finally:
        if ses is not None:
            # ONEMLI: flash'a dokunmadan ONCE kapat.
            ses.deinit()
    if bas >= p:
        bas = 0
    return bloklar, bas, p, tepe


def _blok_akit(ss, bloklar, bas, son):
    """Blok listesinin [bas, son) araligini dogrudan sokete yazar.

    NEDEN FLASH'A YAZMIYORUZ: ses zaten RAM'de. Onu flash'a yazip geri
    okumak saf israfti -- olculdu, 128 KB icin ~1.5 saniye. Yukleme
    bittiginde bloklar zaten birakiliyor.

    NEDEN 4 KB'LIK PARCALAR: her ss.write cagrisi ayri bir TLS kaydi
    (ve genelde ayri bir TCP parcasi) uretiyor. 1 KB ile gonderirken
    yanit suresi 2845 ms olculdu, 4 KB'a cikinca 1103 ms'ye dustu.
    """
    yer = 0
    for b in bloklar:
        n = len(b)
        if yer + n > bas and yer < son:
            a = bas - yer
            if a < 0:
                a = 0
            z = son - yer
            if z > n:
                z = n
            if a == 0 and z == n:
                ss.write(b)
            else:
                ss.write(memoryview(b)[a:z])
            _watchdog_touch()
            _gpt_wait_step()
        yer += n
        if yer >= son:
            break


# ---- yukleme ----

def _yanit_oku(ss, zaman_asimi):
    ham = bytearray()
    basladi = time.ticks_ms()
    while True:
        d = ss.read(512)
        _watchdog_touch()
        if d is None:
            if time.ticks_diff(time.ticks_ms(), basladi) >= zaman_asimi * 1000:
                break
            _gpt_wait_step()
            time.sleep_ms(2)
            continue
        if len(d) == 0:
            break
        ham.extend(d)
        if len(ham) > 60000:
            break
        _gpt_wait_step()
    kes = _buffer_find(ham, b"\r\n\r\n")
    if kes < 0:
        return 0, ""
    bas = bytes(ham[:kes])
    govde = ham[kes + 4:]
    try:
        durum = int(bas.split(b"\r\n")[0].split(b" ")[1])
    except Exception:
        durum = 0
    if bas.lower().find(b"transfer-encoding: chunked") >= 0:
        govde, tam = _dechunk(govde)
        if not tam:
            return 0, ""
    return durum, _decode_buffer(govde)


def baglan():
    """TLS baglantisini KAYITTAN ONCE acar.

    NEDEN: el sikismasi cihazda 2357-2505 ms surtuyor ve govdeyi hic
    beklemiyor. Ekran acilir acilmaz baslatilirsa, kullanici tusa basip
    konusana kadar coktan bitmis olur -- konusma sonrasi beklemeden
    tamamen dusuyor. Ayrica kayit tamponu daha ayrilmadigi icin el
    sikismasi bellegin en bol haliyle karsilanir.
    """
    try:
        gc.collect()
        return tls_connect("api.openai.com", 30)
    except Exception as exc:
        log_error("ses_baglan", exc)
        return None


def _kapat(baglanti):
    if not baglanti:
        return
    for nesne in baglanti:
        if nesne is not None:
            try:
                nesne.close()
            except Exception:
                pass


def _gonder(baglanti, bloklar, bas, son, model):
    """Acik baglanti uzerinden kaydi yollar. (metin, hata) doner."""
    anahtar = OPENAI_API_KEY.strip()
    if not anahtar or anahtar.startswith("sk-BURAYA"):
        return None, "API ANAHTARI GIRILMEMIS"
    ses_boyu = son - bas
    basl = _wav_basligi(ses_boyu)
    sinir = "----masasaatiSES"
    on = (
        "--%s\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n%s\r\n"
        "--%s\r\nContent-Disposition: form-data; name=\"language\"\r\n\r\n%s\r\n"
        "--%s\r\nContent-Disposition: form-data; name=\"file\"; "
        "filename=\"ses.wav\"\r\nContent-Type: audio/wav\r\n\r\n"
        % (sinir, model, sinir, DIL, sinir)).encode("utf-8")
    arka = ("\r\n--%s--\r\n" % sinir).encode("utf-8")
    ss = baglanti[0]
    try:
        ss.write((
            "POST /v1/audio/transcriptions HTTP/1.1\r\n"
            "Host: api.openai.com\r\n"
            "Authorization: Bearer %s\r\n"
            "Content-Type: multipart/form-data; boundary=%s\r\n"
            "Content-Length: %d\r\n"
            "Connection: close\r\n\r\n"
            % (anahtar, sinir,
               len(on) + len(basl) + ses_boyu + len(arka))).encode("utf-8"))
        ss.write(on)
        ss.write(basl)
        _blok_akit(ss, bloklar, bas, son)
        ss.write(arka)
        durum, govde = _yanit_oku(ss, 30)
        if durum != 200 or not govde:
            return None, "SES SUNUCU KODU " + str(durum)
        metin = json.loads(govde).get("text")
        if not metin:
            # Bos metin = konusma duyulmadi. Bu bir ARIZA DEGIL, o yuzden
            # yeniden denenmemeli: denendi ve iki tam tur (7.8 sn) surup
            # yedek modelden anlamsiz metin donduruyordu.
            return "", None
        return metin, None
    except Exception as exc:
        log_error("ses_gonder", exc)
        return None, "BAGLANTI: " + str(exc)


def yaziya_dok(baglanti, bloklar, bas, son):
    metin, hata = (None, "BAGLANTI YOK")
    if baglanti:
        metin, hata = _gonder(baglanti, bloklar, bas, son, MODEL)
        _kapat(baglanti)
    if metin is None:
        # SADECE gercek arizada yeniden denenir (baglanti koptu, sunucu
        # kodu kotu). Onceden acilan baglanti kullanici bekledigi icin
        # kopmus olabilir; ya da model adi hesapta gecersiz olabilir.
        yeni = baglan()
        if yeni:
            metin, hata = _gonder(yeni, bloklar, bas, son, YEDEK_MODEL)
            _kapat(yeni)
    return metin, hata


# ---- ekran ----

_BTN_Y = 205
_KAYIT_X = 60
_KAYIT_W = 200
_KAYIT_H = 54
_KAYIT_Y = 40


def _ekran_ciz(durum):
    lcd.fill(BG)
    lcd.text("SES -> YAZI", 4, 6, TITLE_COL, 2)
    lcd.hline(0, 26, WIDTH, DARKGRAY)
    if durum == "hazir":
        lcd.fill_rect(_KAYIT_X, _KAYIT_Y, _KAYIT_W, _KAYIT_H, GREEN)
        lcd.rect(_KAYIT_X, _KAYIT_Y, _KAYIT_W, _KAYIT_H, GRAY)
        lcd.text("KAYIT", _KAYIT_X + (_KAYIT_W - 5 * 12) // 2,
                 _KAYIT_Y + 19, BLACK, 2)
        lcd.text("SORUNU SOYLE, GPT CEVAPLASIN", 28, 112, GRAY, 1)
        lcd.text("KONUSMAN BITINCE KENDILIGINDEN DURUR", 4, 130, GRAY, 1)
    else:
        lcd.fill_rect(_KAYIT_X, _KAYIT_Y, _KAYIT_W, _KAYIT_H, RED)
        lcd.rect(_KAYIT_X, _KAYIT_Y, _KAYIT_W, _KAYIT_H, GRAY)
        lcd.text("KONUS", _KAYIT_X + (_KAYIT_W - 5 * 12) // 2,
                 _KAYIT_Y + 19, WHITE, 2)
    _mini_saat_kose(_BTN_Y - 12, True)
    lcd.fill_rect(0, _BTN_Y, 100, 32, BLUE)
    lcd.rect(0, _BTN_Y, 100, 32, GRAY)
    lcd.text("GERI", 26, _BTN_Y + 12, WHITE, 1)


def _run():
    apply_ans_size(ans_size_idx)
    while True:
        _ekran_ciz("hazir")
        # TLS el sikismasi BURADA baslar, tusa basilmadan once. Cihazda
        # 2.4 saniye suruyor ve govdeyi hic beklemiyor; kullanici ekrani
        # okuyup tusa basana kadar bitmis oluyor, yani konusma sonrasi
        # beklemeden tamamen dusuyor.
        baglanti = baglan()
        _wait_touch_release()
        sec = None
        while sec is None:
            p = touch.read_fast()
            if p is None:
                _mini_saat_kose(_BTN_Y - 12)
                time.sleep_ms(20)
                continue
            x, y = p
            if y >= _BTN_Y and x < 100:
                _wait_touch_release()
                _kapat(baglanti)
                return None
            if (_KAYIT_X <= x <= _KAYIT_X + _KAYIT_W and
                    _KAYIT_Y <= y <= _KAYIT_Y + _KAYIT_H):
                _wait_touch_release()
                sec = "kayit"

        _ekran_ciz("kayit")
        bloklar = None
        try:
            # BASILI TUTMA KULLANILMIYOR. Denendi ve kotu calisti: direncli
            # dokunmatik SUREKLI basili parmagi guvenilir okumuyor, arada
            # bosluk veriyor ve kayit erken kesiliyordu. Fiziksel bir tus
            # eklenince basili tutma tekrar acilabilir -- gercek bir tus
            # temiz ve kesintisiz sinyal verir.
            bloklar, bas, son, tepe = kaydet()
        except Exception as exc:
            log_error("ses_kaydet", exc)
            _kapat(baglanti)
            _sonuc_goster(None, "MIKROFON HATASI")
            continue
        try:
            if son - bas < ORNEK_HIZ:          # yarim saniyeden kisa
                _kapat(baglanti)
                _sonuc_goster(None, "KAYIT COK KISA")
                continue
            if tepe < 800:
                _kapat(baglanti)
                _sonuc_goster(None, "SES DUYULMADI")
                continue
            metin = None
            hata = None
            lcd.fill(BG)
            lcd.text("SES -> YAZI", 4, 6, TITLE_COL, 2)
            lcd.hline(0, 26, WIDTH, DARKGRAY)
            lcd.text("YAZIYA DOKULUYOR...", 76, 110, GRAY, 1)
            _gpt_wait_start()
            try:
                metin, hata = yaziya_dok(baglanti, bloklar, bas, son)
            finally:
                _gpt_wait_stop()
        finally:
            # Ses RAM'de duruyor; cevap ekrani cizilmeden birakilmali.
            bloklar = None
            gc.collect()
        if metin == "":
            metin, hata = None, "SES ANLASILAMADI"
        if metin:
            # Metin dogrudan dondurulur; cagiran taraf onu GPT'ye sorar.
            # Duyulan cumle cevap ekraninin basliginda gorunuyor, yani
            # yanlis anlasildiysa kullanici hemen fark eder.
            return metin
        if _sonuc_goster(None, hata) == "back":
            return None


def _sonuc_goster(metin, hata):
    set_answer_header("SES -> YAZI", hata is not None)
    set_answer_text_color(RED if hata is not None else FG)
    ham = hata if hata is not None else metin
    satirlar = wrap_full(to_screen_text(ham),
                         (WIDTH - 8) // SIZE_PROFILES[ans_size_idx][2])
    if not satirlar:
        satirlar = [""]
    sonuc = show_answer(satirlar)
    release_answer_buffers()
    return sonuc
