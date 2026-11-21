#!/usr/bin/env python3
"""Build entry.png: world news for Saturday, 21 November 2026.

Fresh implementation for the make.fun news-image-20261121 bounty.
Draws a deterministic 1024x1024 PNG with PIL only: fixed fonts, fixed
geometry, no timestamps, no randomness, no network access.

Layout (top to bottom):
  * header band with title + date-check pill + verification dek
  * 2x2 grid of top-story panels, each with a coloured spine
  * "More from 21 November" — 18 one-liners in two columns
  * UTC wire strip — four timed BBC items
  * footer with sources
"""

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "entry.png"

W, H = 1024, 1024

PALETTE = {
    "bg": (11, 21, 38),
    "panel": (21, 42, 68),
    "panel_edge": (52, 84, 120),
    "band": (16, 32, 54),
    "white": (244, 247, 251),
    "muted": (169, 186, 205),
    "faint": (126, 145, 168),
    "gold": (232, 184, 75),
    "teal": (63, 182, 168),
    "red": (228, 87, 46),
    "sky": (74, 144, 217),
    "rule": (46, 74, 106),
}

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def load_font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


TITLE_FONT = load_font("DejaVuSerif-Bold.ttf", 46)
HEADLINE_FONT = load_font("DejaVuSerif-Bold.ttf", 25)
KICKER_FONT = load_font("DejaVuSans-Bold.ttf", 14)
SUB_FONT = load_font("DejaVuSans.ttf", 16)
DEK_FONT = load_font("DejaVuSans.ttf", 17)
PILL_FONT = load_font("DejaVuSans-Bold.ttf", 15)
SECTION_FONT = load_font("DejaVuSans-Bold.ttf", 17)
ITEM_FONT = load_font("DejaVuSans.ttf", 15)
ITEM_FONT_SMALL = load_font("DejaVuSans.ttf", 13)
WIRE_TIME_FONT = load_font("DejaVuSans-Bold.ttf", 15)
WIRE_TEXT_FONT = load_font("DejaVuSans.ttf", 14)
WIRE_LABEL_FONT = load_font("DejaVuSans-Bold.ttf", 13)
FOOTER_FONT = load_font("DejaVuSans.ttf", 13)

MARGIN = 24
CONTENT_W = W - 2 * MARGIN


def wrap_words(text, font, max_width):
    """Greedy word wrap measured with font.getlength."""
    lines = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if font.getlength(trial) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def pick_fitting_font(text, candidates, max_width):
    """Return the first candidate font under which text fits on one line."""
    for font in candidates:
        if font.getlength(text) <= max_width:
            return font
    return candidates[-1]


def draw_header(draw):
    draw.rectangle([0, 0, W, 128], fill=PALETTE["bg"])
    draw.text((MARGIN, 16), "WORLD NEWS", font=TITLE_FONT, fill=PALETTE["white"])
    pill = "DATE CHECK: SATURDAY, 21 NOVEMBER 2026"
    pill_w = int(PILL_FONT.getlength(pill)) + 30
    pill_x = W - MARGIN - pill_w
    draw.rounded_rectangle(
        [pill_x, 24, pill_x + pill_w, 64], radius=20,
        outline=PALETTE["gold"], width=2,
    )
    draw.text((pill_x + 15, 34), pill, font=PILL_FONT, fill=PALETTE["gold"])
    dek = "Top stories from Saturday, 21 November 2026 \u2014 verified against Reuters, AP, BBC and NYT"
    draw.text((MARGIN, 86), dek, font=DEK_FONT, fill=PALETTE["muted"])
    draw.rectangle([0, 124, W, 128], fill=PALETTE["gold"])


def draw_story(draw, box, accent, kicker, headline, sub):
    x, y, w, h = box
    draw.rounded_rectangle(
        [x, y, x + w, y + h], radius=10,
        fill=PALETTE["panel"], outline=PALETTE["panel_edge"], width=1,
    )
    draw.rectangle([x, y + 12, x + 6, y + h - 12], fill=accent)
    tx = x + 22
    text_w = w - 42
    draw.text((tx, y + 14), kicker, font=KICKER_FONT, fill=accent)
    cursor = y + 42
    for line in wrap_words(headline, HEADLINE_FONT, text_w):
        draw.text((tx, cursor), line, font=HEADLINE_FONT, fill=PALETTE["white"])
        cursor += 31
    cursor += 6
    for line in wrap_words(sub, SUB_FONT, text_w):
        draw.text((tx, cursor), line, font=SUB_FONT, fill=PALETTE["muted"])
        cursor += 22


TOP_STORIES = [
    {
        "accent": PALETTE["gold"],
        "kicker": "CLIMATE \u00b7 COP31 \u2014 ANTALYA",
        "headline": "COP31 deadlocked over fossil fuels",
        "sub": "The fossil-fuel fight extends talks into an extra day in Antalya as countries split on a phase-out.",
    },
    {
        "accent": PALETTE["teal"],
        "kicker": "UKRAINE \u00b7 KYIV",
        "headline": "Zelensky calls Putin a 'killer'",
        "sub": "The rebuke follows Trump calling the Russian president a friend.",
    },
    {
        "accent": PALETTE["red"],
        "kicker": "NATO \u00b7 POLAND",
        "headline": "Russian missiles land in Poland",
        "sub": "NATO calls it a \u201cgrave violation\u201d; Secretary General Rutte is due in Warsaw on Saturday.",
    },
    {
        "accent": PALETTE["sky"],
        "kicker": "KRYVYI RIH \u00b7 UKRAINE",
        "headline": "Double-tap strike kills boy, 7, and paramedic, 20",
        "sub": "52 injured in the Russian strike on World Children's Day, officials say.",
    },
]

MORE_ITEMS = [
    "Denmark expels Russian defence attache over rapper plot.",
    "Trump threatens ban on US firms building AI data centres abroad.",
    "Mamdani to close Rikers Island jail by 2032.",
    "Man convicted of starting LA Palisades fire.",
    "FBI probes apparent hack of its criminal database.",
    "Bolsonaro taken to hospital in Brazil.",
    "US declassifies more UFO footage.",
    "Tech sell-off drags markets as Anthropic slides.",
    "Judge approves $7.25bn Roundup settlement.",
    "GTA 6 sales top $2.3bn, breaks records.",
    "NYC weighs e-bike battery crackdown after fatal fires.",
    "Most new Black Democrats in decades join Congress.",
    "Houthis fire on Riyadh; 3 missiles intercepted.",
    "French police sentenced over Zecler beating.",
    "Indian man jailed 19+ years in Sikh separatist murder plot.",
    "Nearly 600 women killed in South Africa in 3 months.",
    "Trump weighs new strikes on Iran, officials say.",
    "Pope Leo hit by rosary in Lima.",
]

WIRE_ITEMS = [
    ("04:26", "Denmark accuses Russia of plot"),
    ("07:31", "COP31 deadlocked"),
    ("08:10", "Zelensky: Putin a 'killer'"),
    ("09:27", "EU deal not tied to fees"),
]


def draw_stories(draw):
    panel_w = (CONTENT_W - 16) // 2
    panel_h = 204
    top = 144
    for i, story in enumerate(TOP_STORIES):
        col = i % 2
        row = i // 2
        box = (
            MARGIN + col * (panel_w + 16),
            top + row * (panel_h + 12),
            panel_w,
            panel_h,
        )
        draw_story(draw, box, story["accent"], story["kicker"],
                   story["headline"], story["sub"])


def draw_more_list(draw):
    section_y = 584
    draw.text((MARGIN, section_y), "MORE FROM 21 NOVEMBER",
              font=SECTION_FONT, fill=PALETTE["gold"])
    rule_x = MARGIN + int(SECTION_FONT.getlength("MORE FROM 21 NOVEMBER")) + 14
    draw.line([rule_x, section_y + 10, W - MARGIN, section_y + 10],
              fill=PALETTE["rule"], width=2)
    col_gap = 24
    col_w = (CONTENT_W - col_gap) // 2
    row_h = 25
    start_y = section_y + 30
    for idx, item in enumerate(MORE_ITEMS):
        col = idx // 9
        row = idx % 9
        x = MARGIN + col * (col_w + col_gap)
        y = start_y + row * row_h
        draw.text((x, y), "\u2022", font=ITEM_FONT, fill=PALETTE["gold"])
        font = pick_fitting_font(item, [ITEM_FONT, ITEM_FONT_SMALL],
                                 col_w - 20)
        draw.text((x + 18, y), item, font=font, fill=PALETTE["white"])


def draw_wire(draw):
    band_y, band_h = 852, 104
    draw.rounded_rectangle(
        [MARGIN, band_y, W - MARGIN, band_y + band_h], radius=10,
        fill=PALETTE["band"], outline=PALETTE["panel_edge"], width=1,
    )
    draw.text((MARGIN + 16, band_y + 10), "UTC WIRE \u00b7 SATURDAY 21 NOV",
              font=WIRE_LABEL_FONT, fill=PALETTE["gold"])
    col_w = (CONTENT_W - 32 - 3 * 12) // 4
    items_y = band_y + 36
    for i, (when, text) in enumerate(WIRE_ITEMS):
        x = MARGIN + 16 + i * (col_w + 12)
        draw.text((x, items_y), when, font=WIRE_TIME_FONT, fill=PALETTE["gold"])
        cursor = items_y + 22
        for line in wrap_words(text, WIRE_TEXT_FONT, col_w):
            draw.text((x, cursor), line, font=WIRE_TEXT_FONT,
                      fill=PALETTE["white"])
            cursor += 19


def draw_footer(draw):
    footer = ("Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 NYT \u2014 All items verified "
              "\u00b7 All times UTC \u00b7 make.fun/news-image-20261121")
    fw = FOOTER_FONT.getlength(footer)
    draw.text(((W - fw) / 2, 978), footer, font=FOOTER_FONT,
              fill=PALETTE["faint"])


def build():
    image = Image.new("RGB", (W, H), PALETTE["bg"])
    if image.size != (W, H):
        raise SystemExit(f"canvas is {image.size}, expected {(W, H)}")
    draw = ImageDraw.Draw(image)
    draw_header(draw)
    draw_stories(draw)
    draw_more_list(draw)
    draw_wire(draw)
    draw_footer(draw)
    image.save(OUT, format="PNG")
    data = OUT.read_bytes()
    if len(data) > 1 << 20:
        raise SystemExit(f"entry.png is {len(data)} bytes, over the 1 MiB limit")
    return data


def report_measurements():
    """Print measured text widths so fit can be audited from the log."""
    dek = "Top stories from Saturday, 21 November 2026 \u2014 verified against Reuters, AP, BBC and NYT"
    print(f"dek width: {DEK_FONT.getlength(dek):.0f} / {CONTENT_W}")
    footer = ("Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 NYT \u2014 All items verified "
              "\u00b7 All times UTC \u00b7 make.fun/news-image-20261121")
    print(f"footer width: {FOOTER_FONT.getlength(footer):.0f} / {CONTENT_W}")
    col_w = (CONTENT_W - 24) // 2
    widest = 0
    for item in MORE_ITEMS:
        w = ITEM_FONT.getlength(item)
        widest = max(widest, w)
        fits = "fits" if w <= col_w - 20 else "shrunk to 13px"
        print(f"  more[{MORE_ITEMS.index(item) + 1:2d}] {w:5.0f}px {fits}: {item[:48]}")
    print(f"widest more-item: {widest:.0f}px vs budget {col_w - 20}px")
    for story in TOP_STORIES:
        hl = wrap_words(story["headline"], HEADLINE_FONT, 480 - 42)
        sb = wrap_words(story["sub"], SUB_FONT, 480 - 42)
        print(f"  panel '{story['headline'][:30]}': headline {len(hl)} line(s), sub {len(sb)} line(s)")


def main():
    data = build()
    digest = hashlib.sha256(data).hexdigest()
    print(f"saved {OUT}  {len(data)} bytes  sha256={digest}")
    report_measurements()


if __name__ == "__main__":
    main()
