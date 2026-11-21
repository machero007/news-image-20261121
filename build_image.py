#!/usr/bin/env python3
"""Build the 21 Nov 2026 world-news summary image (1024x1024 PNG).

Dense editorial poster: date header, 2x2 panels of the day's biggest
stories (each a simple drawn scene + headline), a "More from
21 November" list of 18 further verified stories, a UTC wire strip and
a footer ticker. Deterministic output: same bytes every run.

News verified 21 Nov 2026 (WITA) against Reuters / AP / BBC / NYT /
WSJ / Independent digests of 21 Nov 2026 reporting.
Panels:
 1. COP31 climate talks in Antalya deadlocked over fossil fuels,
    running into an extra day (AP/BBC).
 2. Zelensky calls Putin a 'killer' after Trump calls the Russian
    leader a friend and hails 'fantastic' ties with Putin and Xi
    (BBC).
 3. Russian missiles land in Poland during the Ukraine barrage;
    NATO calls it a 'grave violation', Rutte due in Warsaw on
    Saturday (AP/BBC/Independent).
 4. Russian double-tap strike on Kryvyi Rih kills a 7-year-old boy
    and a 20-year-old paramedic, 52 injured, on World Children's
    Day (Independent/Kyiv Independent).
More (18): Denmark expels Russian defence attache over rapper
assassination plot (Reuters/BBC); Trump threatens ban on US firms
building AI data centres overseas (BBC/AP); Mamdani to close Rikers
Island jail by 2032 (BBC/AP); man convicted of starting LA Palisades
fire (BBC); FBI probes apparent hack of its criminal database (BBC);
Bolsonaro taken to hospital in Brazil (BBC); US declassifies more UFO
footage (BBC); tech sell-off drags markets as Anthropic slides (BBC);
judge approves $7.25bn Roundup settlement (AP/BBC); GTA 6 sales top
$2.3bn (BBC); NYC weighs e-bike battery crackdown after fatal fires
(Reuters); most new Black Democrats in decades join Congress
(Reuters); Houthis fire on Riyadh, 3 missiles intercepted (Horizon);
French police sentenced over Zecler beating (BBC); Indian man jailed
19+ years in Sikh separatist murder plot (BBC); nearly 600 women
killed in South Africa in 3 months (BBC); Trump weighs new strikes
on Iran, officials say (NYT); Pope Leo hit by rosary in Lima (AP).
UTC wire times are BBC publication timestamps (UTC) for 21 Nov 2026:
Denmark plot 04:26; COP31 deadlock 07:31; Zelensky 'killer' 08:10;
Miliband EU deal 09:27.
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

NAVY = (13, 27, 46)
PANEL = (22, 40, 63)
WHITE = (245, 245, 240)
GOLD = (212, 175, 55)
MUTE = (170, 185, 200)
RED = (198, 60, 48)
ORANGE = (224, 122, 42)
TEAL = (46, 160, 140)
BLUE = (70, 130, 200)
SKY = (38, 68, 102)

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


img = Image.new("RGB", (W, H), NAVY)
d = ImageDraw.Draw(img)

# ---------- header ----------
d.text((24, 16), "THE WORLD  \u2022  SATURDAY", font=font(FB, 24), fill=GOLD)
d.text((24, 42), "21 NOVEMBER 2026", font=font(FB, 62), fill=WHITE)
d.text((24, 112), "One day, one image \u2014 the news that mattered most.",
       font=font(FR, 21), fill=MUTE)
d.line([(24, 140), (1000, 140)], fill=GOLD, width=3)

# ---------- panels ----------
PX, PY, PW, PH, GAP = 24, 150, 488, 268, 16
ART_H = 140  # art drawn at 488x196, resized to 488x140


def panel(x, y, accent):
    d.rounded_rectangle([x, y, x + PW, y + PH], radius=14, fill=PANEL)
    d.rounded_rectangle([x, y, x + PW, y + 10], radius=5, fill=accent)
    d.rounded_rectangle([x, y + 5, x + PW, y + 10], fill=accent)


# Captions: every sub measured BEFORE finalizing (lesson from 18 Nov:
# subs must be <=450px at DejaVu 22; headline lines <=456px at Bold 29).
CAPTIONS = [
    ("COP31 DEADLOCK",
     "Fossil-fuel fight extends talks"),
    ("ZELENSKY: PUTIN IS A 'KILLER'",
     "After Trump calls Putin a friend"),
    ("MISSILES HIT POLAND",
     "NATO: 'grave violation' of airspace"),
    ("DOUBLE-TAP KILLS BOY, 7",
     "Kryvyi Rih: child, paramedic dead"),
]


def caption(x, y, headline, sub, accent):
    f_h, f_s = font(FB, 29), font(FR, 22)
    lines = wrap(d, headline, f_h, PW - 32)
    for ln in lines:
        assert d.textlength(ln, font=f_h) <= PW - 32, \
            "headline too wide: %r" % ln
    assert d.textlength(sub, font=f_s) <= 450, \
        "sub too wide (%dpx): %r" % (d.textlength(sub, font=f_s), sub)
    cy = y + PH - 112
    for ln in lines[:2]:
        d.text((x + 16, cy), ln, font=f_h, fill=WHITE)
        cy += 34
    d.text((x + 16, y + PH - 40), sub, font=f_s, fill=MUTE)
    print("caption OK: %r sub=%dpx" % (headline,
          d.textlength(sub, font=f_s)))


def burst(dr, cx, cy, r, color):
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    dr.polygon(pts, fill=color)


def render_art(art_fn, x, y):
    """Draw art at 488x196, then paste resized to 488x140 (deterministic)."""
    tmp = Image.new("RGB", (PW, 196), PANEL)
    ad = ImageDraw.Draw(tmp)
    art_fn(ad, 0, 0)
    img.paste(tmp.resize((PW, ART_H), Image.LANCZOS), (x, y + 10))


# --- Panel 1 art: COP31 - globe, smokestacks, thermometer ---
def art1(dr, x, y):
    dr.rectangle([x, y + 10, x + PW, y + 196], fill=(30, 60, 48))
    # sun
    dr.ellipse([x + 400, y + 24, x + 448, y + 72], fill=(255, 210, 90))
    # globe
    dr.ellipse([x + 60, y + 44, x + 220, y + 196 - 20], fill=(40, 110, 170))
    dr.ellipse([x + 84, y + 62, x + 130, y + 100], fill=(60, 150, 80))
    dr.ellipse([x + 140, y + 104, x + 196, y + 140], fill=(60, 150, 80))
    dr.ellipse([x + 96, y + 130, x + 140, y + 162], fill=(60, 150, 80))
    # smokestacks
    for sx in (270, 310, 350):
        dr.rectangle([x + sx, y + 90, x + sx + 26, y + 176],
                     fill=(70, 70, 78))
    dr.ellipse([x + 276, y + 56, x + 306, y + 82], fill=(150, 150, 155))
    dr.ellipse([x + 318, y + 44, x + 348, y + 70], fill=(165, 165, 170))
    dr.ellipse([x + 356, y + 58, x + 384, y + 84], fill=(150, 150, 155))
    # thermometer
    dr.rectangle([x + 428, y + 110, x + 444, y + 168], fill=(230, 230, 230))
    dr.ellipse([x + 420, y + 158, x + 452, y + 188], fill=(230, 230, 230))
    dr.rectangle([x + 432, y + 128, x + 440, y + 168], fill=(220, 50, 40))
    dr.ellipse([x + 426, y + 162, x + 446, y + 182], fill=(220, 50, 40))
    dr.text((x + 16, y + 24), "TALKS RUN INTO OVERTIME",
            font=font(FB, 24), fill=(255, 220, 120))


# --- Panel 2 art: three flags + speech bubble ---
def art2(dr, x, y):
    dr.rectangle([x, y + 10, x + PW, y + 196], fill=(52, 74, 96))
    # US flag
    fx = x + 40
    dr.line([(fx, y + 60), (fx, y + 160)], fill=(200, 200, 200), width=4)
    for i in range(7):
        dr.rectangle([fx, y + 62 + i * 8, fx + 110, y + 62 + i * 8 + 8],
                     fill=(190, 30, 40) if i % 2 == 0 else WHITE)
    dr.rectangle([fx, y + 62, fx + 46, y + 62 + 32], fill=(20, 40, 110))
    # Ukraine flag
    fx = x + 190
    dr.line([(fx, y + 60), (fx, y + 160)], fill=(200, 200, 200), width=4)
    dr.rectangle([fx, y + 62, fx + 110, y + 62 + 28], fill=(40, 110, 200))
    dr.rectangle([fx, y + 90, fx + 110, y + 118], fill=(255, 215, 0))
    # Russia flag
    fx = x + 340
    dr.line([(fx, y + 60), (fx, y + 160)], fill=(200, 200, 200), width=4)
    dr.rectangle([fx, y + 62, fx + 110, y + 62 + 19], fill=WHITE)
    dr.rectangle([fx, y + 81, fx + 110, y + 100], fill=(30, 60, 180))
    dr.rectangle([fx, y + 100, fx + 110, y + 118], fill=(200, 30, 30))
    # speech bubble
    dr.rounded_rectangle([x + 180, y + 128, x + 330, y + 176], radius=12,
                         fill=WHITE)
    dr.polygon([(x + 210, y + 176), (x + 230, y + 196), (x + 240, y + 176)],
               fill=WHITE)
    dr.text((x + 196, y + 138), "\"KILLER\"", font=font(FB, 30),
            fill=(200, 30, 30))
    dr.text((x + 16, y + 24), "TRUMP: 'FANTASTIC' TIES",
            font=font(FB, 24), fill=(255, 220, 120))


# --- Panel 3 art: night sky, missile trails over Poland ---
def art3(dr, x, y):
    dr.rectangle([x, y + 10, x + PW, y + 196], fill=(18, 22, 40))
    # stars
    for sx, sy in [(40, 40), (120, 28), (210, 52), (300, 30), (380, 44),
                   (450, 30), (90, 70), (250, 70), (420, 68)]:
        dr.ellipse([x + sx, y + sy, x + sx + 4, y + sy + 4],
                   fill=(240, 240, 220))
    # missile trails arcing down (start below the overlay text)
    for tx, ty, ex, ey in [(60, 52, 180, 150), (260, 52, 350, 150),
                           (400, 52, 440, 150)]:
        dr.line([(x + tx, y + ty), (x + ex, y + ey)], fill=(255, 200, 90),
                width=3)
        dr.ellipse([x + tx - 4, y + ty - 4, x + tx + 4, y + ty + 4],
                   fill=(255, 240, 180))
    # ground
    dr.rectangle([x, y + 150, x + PW, y + 196], fill=(40, 55, 40))
    # explosions where missiles land
    burst(dr, x + 180, y + 150, 24, (255, 200, 60))
    burst(dr, x + 180, y + 150, 13, (255, 110, 40))
    burst(dr, x + 350, y + 150, 20, (255, 190, 70))
    burst(dr, x + 350, y + 150, 11, (255, 120, 40))
    # NATO compass star shield
    dr.ellipse([x + 408, y + 108, x + 470, y + 170], fill=(20, 40, 90))
    dr.ellipse([x + 408, y + 108, x + 470, y + 170], outline=GOLD, width=2)
    burst(dr, x + 439, y + 139, 18, GOLD)
    dr.text((x + 16, y + 24), "NATO: GRAVE VIOLATION",
            font=font(FB, 24), fill=(255, 120, 100))


# --- Panel 4 art: Kryvyi Rih at night, ambulance, explosion ---
def art4(dr, x, y):
    dr.rectangle([x, y + 10, x + PW, y + 196], fill=(30, 34, 52))
    for bx, bw, bh in [(20, 60, 70), (95, 45, 95), (150, 70, 60),
                       (340, 55, 85), (410, 60, 65)]:
        dr.rectangle([x + bx, y + 120 - bh, x + bx + bw, y + 120],
                     fill=(18, 20, 34))
        for wy in range(y + 120 - bh + 8, y + 116, 18):
            for wx in range(x + bx + 6, x + bx + bw - 6, 14):
                dr.rectangle([wx, wy, wx + 5, wy + 7], fill=(255, 210, 90))
    # street
    dr.rectangle([x, y + 120, x + PW, y + 196], fill=(45, 45, 55))
    # explosion over a building (left, clear of the overlay text)
    burst(dr, x + 120, y + 70, 30, (255, 200, 60))
    burst(dr, x + 120, y + 70, 16, (255, 110, 40))
    dr.ellipse([x + 140, y + 40, x + 175, y + 68], fill=(130, 130, 135))
    # ambulance
    dr.rectangle([x + 60, y + 140, x + 170, y + 176], fill=WHITE)
    dr.rectangle([x + 150, y + 148, x + 196, y + 176], fill=WHITE)
    dr.rectangle([x + 96, y + 150, x + 108, y + 168], fill=(200, 30, 30))
    dr.rectangle([x + 90, y + 156, x + 114, y + 162], fill=(200, 30, 30))
    dr.ellipse([x + 78, y + 172, x + 96, y + 188], fill=(20, 20, 20))
    dr.ellipse([x + 160, y + 172, x + 178, y + 188], fill=(20, 20, 20))
    dr.text((x + 200, y + 24), "WORLD CHILDREN'S DAY",
            font=font(FB, 20), fill=(255, 120, 100))


x, y = PX, PY
panel(x, y, TEAL)
render_art(art1, x, y)
caption(x, y, *CAPTIONS[0], TEAL)

x, y = PX + PW + GAP, PY
panel(x, y, GOLD)
render_art(art2, x, y)
caption(x, y, *CAPTIONS[1], GOLD)

x, y = PX, PY + PH + GAP
panel(x, y, RED)
render_art(art3, x, y)
caption(x, y, *CAPTIONS[2], RED)

x, y = PX + PW + GAP, PY + PH + GAP
panel(x, y, ORANGE)
render_art(art4, x, y)
caption(x, y, *CAPTIONS[3], ORANGE)

# ---------- More from 21 November: 18 further verified stories ----------
d.line([(24, 706), (1000, 706)], fill=GOLD, width=2)
d.text((24, 714), "MORE FROM 21 NOVEMBER  \u2022  DATE CHECK: SATURDAY, "
       "21 NOVEMBER 2026", font=font(FB, 18), fill=GOLD)

MORE_A = [
    "Denmark expels Russian attache over rapper plot",
    "Trump threatens ban on AI data centres abroad",
    "Mamdani to close Rikers Island jail by 2032",
    "Man convicted of starting LA Palisades fire",
    "FBI probes apparent hack of criminal database",
    "Bolsonaro taken to hospital in Brazil",
    "US declassifies more UFO footage",
    "Tech sell-off drags markets as Anthropic slides",
    "Judge approves $7.25bn Roundup settlement",
]
MORE_B = [
    "GTA 6 sales top $2.3bn, breaks records",
    "NYC weighs e-bike battery crackdown after fires",
    "Most new Black Democrats in decades join Congress",
    "Houthis fire on Riyadh; 3 missiles intercepted",
    "French police sentenced over Zecler beating",
    "Indian man jailed 19+ yrs in Sikh murder plot",
    "Nearly 600 women killed in South Africa in 3 months",
    "Trump weighs new strikes on Iran, officials say",
    "Pope Leo hit by rosary in Lima",
]
assert len(MORE_A) == 9 and len(MORE_B) == 9
f_m = font(FR, 14)
f_bullet = font(FB, 14)
for col_x, items in ((24, MORE_A), (512, MORE_B)):
    for i, item in enumerate(items):
        yy = 742 + i * 17
        assert d.textlength(item, font=f_m) <= 470, \
            "more-item too wide (%dpx): %r" % (d.textlength(item,
                                                           font=f_m), item)
        d.text((col_x, yy), "\u2022", font=f_bullet, fill=GOLD)
        d.text((col_x + 16, yy), item, font=f_m, fill=WHITE)
print("more section OK: %d items" % (len(MORE_A) + len(MORE_B)))

# ---------- UTC wire strip ----------
wire = ("UTC WIRE  \u2014  04:26 Denmark accuses Russia of plot  "
        "\u2022  07:31 COP31 deadlocked  \u2022  08:10 Zelensky: Putin "
        "a 'killer'  \u2022  09:27 EU deal not tied to fees")
f_w = font(FR, 13)
assert d.textlength(wire, font=f_w) <= 976, "wire too wide"
d.text((24, 902), wire, font=f_w, fill=MUTE)
print("wire OK: %dpx" % d.textlength(wire, font=f_w))

# ---------- footer ticker ----------
d.line([(24, 922), (1000, 922)], fill=GOLD, width=2)
f_f = font(FR, 22)
ticker = ("ALSO:  Trump threatens AI data-centre ban  \u2022  Mamdani "
          "to close Rikers by 2032  \u2022  GTA 6 sales top $2.3bn")
tlines = wrap(d, ticker, f_f, 976)
assert len(tlines) <= 2, "ticker wraps to %d lines: %r" % (len(tlines),
                                                          tlines)
for i, ln in enumerate(tlines):
    d.text((24, 930 + i * 26), ln, font=f_f, fill=MUTE)
d.text((24, 988), "Sources: Reuters / AP / BBC / NYT / WSJ / Independent "
       "\u2014 21 Nov 2026", font=font(FR, 19), fill=(120, 135, 150))

img.save(OUT, "PNG", optimize=True)
print("saved", OUT, os.path.getsize(OUT), "bytes", img.size)
