#!/usr/bin/env python3
"""Render the 23 November 2026 world-news front page as a 1024x1024 PNG.

Layout (built fresh for this edition): masthead with a red rule, a
full-width lead headline on the COP31 collapse with two text columns
below it (climate left, Gulf right) plus a verdict strip, a dark
markets band with a horizontal bar chart of Friday's rout, a 2x3 grid
of story cards, and a navy ticker footer.
Deterministic: no clock or random data inside the image, fixed fonts
and geometry. Every line is wrapped to its box; nothing is clipped.

Stories verified 23 Nov 2026 (Reuters, AP, CNN, BBC, AFP, ATP Tour):
COP31 collapsed Sunday in Antalya; Gulf war around Hormuz; Friday
20 Nov market rout; Dymer drone strike; Sparta II fire; Russian
missiles into Poland + NATO meeting today; Banten factory fire;
ICJ Rohingya genocide ruling (Thu 19 Nov); Alcaraz wins ATP Finals;
Belgium flight shutdown today; Nepal PM in Delhi; South Korea
minister resigns; India 720/9 in Wellington; Van Gogh $190.4m.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

INK = (20, 20, 22)
PAPER = (251, 249, 244)
RED = (176, 32, 26)
NAVY = (15, 40, 88)
DARK = (22, 26, 36)
GREY = (96, 96, 100)
RULE = (178, 172, 162)
CARD = (255, 255, 255)
TEAL = (13, 104, 90)
GOLD = (255, 208, 88)
BAR = (255, 106, 96)
PALE = (206, 206, 212)


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, text, fnt, width, leading, fill=INK, cap=None):
    lines = wrap(d, text, fnt, width)
    if cap:
        lines = lines[:cap]
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(d, x0, x1, y, fill=INK, w=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---------------- masthead ----------------
d.rectangle([0, 0, W, 10], fill=RED)
d.text((32, 24), "THE WORLD IN ONE PAGE", font=F(SERIF_B, 50), fill=INK)
d.text((32, 84), "MONDAY, 23 NOVEMBER 2026", font=F(SANS_B, 24), fill=RED)
d.text((32, 116),
       "14 stories from one day  •  Antalya  •  Hormuz  •  Kyiv  •  The Hague  •  Turin",
       font=F(SANS, 17), fill=GREY)
d.text((W - 32, 84), "No. 23", font=F(SERIF_B, 24), fill=INK, anchor="ra")
d.text((W - 32, 116), "MONDAY EDITION", font=F(SANS, 15), fill=GREY, anchor="ra")
rule(d, 32, W - 32, 146, fill=INK, w=3)
rule(d, 32, W - 32, 152, fill=INK, w=1)

# ---------------- lead: COP31 collapse ----------------
LY = 164
d.text((32, LY), "CLIMATE  •  THE LEAD STORY", font=F(SANS_B, 17), fill=TEAL)
y = block(d, 32, LY + 26,
          "COP31 COLLAPSES IN ANTALYA — NO CLIMATE DEAL",
          F(SERIF_B, 30), 960, 36, cap=2)
y += 4
d.text((32, y), "The longest summit in history ends without a pact — the first major breakdown since Copenhagen in 2009.",
       font=F(SANS, 17), fill=GREY)
y += 24
# two columns: climate detail (left) / Gulf (right)
COL_Y = y
d.text((32, COL_Y), "WHAT HAPPENED", font=F(SANS_B, 15), fill=TEAL)
y1 = block(d, 32, COL_Y + 24,
           "After two days of overtime, COP31 presidents put the “Antalya Pact” "
           "to nearly 200 nations on Sunday — and the EU, Britain, Panama and "
           "others rejected it, because it never named fossil fuels. A $120bn "
           "finance target was dropped too.",
           F(SANS, 17), 590, 22, cap=4)
d.line([(652, COL_Y), (652, COL_Y + 128)], fill=RULE, width=1)
d.text((672, COL_Y), "THE GULF  •  WAR", font=F(SANS_B, 15), fill=RED)
y2 = block(d, 672, COL_Y + 24,
           "Iran's war with the U.S. and Israel, now in its ninth month, still "
           "rages around the Strait of Hormuz. Houthi missiles fired at Saudi "
           "Arabia were intercepted; Qatar-mediated talks have stalled.",
           F(SANS, 15), 320, 20, cap=5)
# verdict strip
VY = COL_Y + 132
d.rectangle([32, VY, W - 32, VY + 30], outline=RED, width=2)
d.text((44, VY + 7), "VERDICT IN ANTALYA:  44 HOURS OF OVERTIME  •  NO CONSENSUS  •  PARIS DEAL STILL STANDS",
       font=F(SANS_B, 14), fill=RED)

rule(d, 32, W - 32, 462, fill=INK, w=2)

# ---------------- markets band ----------------
d.rectangle([0, 472, W, 566], fill=DARK)
d.text((32, 482), "FRIDAY'S ROUT: THE AI TRADE UNRAVELS", font=F(SANS_B, 20), fill=(255, 255, 255))
d.text((32, 508), "The S&P 500 fell 3.7% on Friday, its worst week since March 2020.",
       font=F(SANS, 15), fill=PALE)
d.text((32, 527), "Nasdaq 100 is in a bear market; world stocks fell 7 days in a row.",
       font=F(SANS, 15), fill=PALE)
d.text((32, 546), "Tokyo is closed today for a holiday. Bitcoin near $59,900.",
       font=F(SANS, 15), fill=PALE)
# Friday drops, biggest first
drops = [("TAIWAN", "-6.2%", 6.2),
         ("NASDAQ", "-5.3%", 5.3),
         ("KOSPI", "-5.2%", 5.2),
         ("NIKKEI", "-5.1%", 5.1),
         ("S&P 500", "-3.7%", 3.7)]
BX, BW = 640, 200
for i, (name, val, mag) in enumerate(drops):
    by = 480 + i * 17
    d.text((560, by), name, font=F(SANS_B, 12), fill=PALE)
    bw = int(BW * mag / 6.2)
    d.rectangle([BX, by + 1, BX + bw, by + 12], fill=BAR)
    d.text((BX + bw + 6, by), val, font=F(SANS_B, 12), fill=(255, 255, 255))

# ---------------- 2x3 card grid ----------------
cards = [
    ("UKRAINE  •  WAR", "14 missing as drone flattens Kyiv flats",
     "A Russian drone struck a five-storey block in Dymer, north of Kyiv, "
     "on Sunday morning. One body was recovered; 14 people, including two "
     "children, are unaccounted for. Nine were evacuated."),
    ("BALTIC  •  SHADOW WAR", "Burning Russian ship towed from Finnish waters",
     "The sanctioned cargo ship Sparta II, hit by drones on Saturday, was "
     "still smouldering on Sunday as Finland, Estonia and Russia fought "
     "the fire together. All 16 crew were evacuated."),
    ("NATO  •  POLAND", "NATO meets today after missiles land in Poland",
     "Three Russian Kh-101 missiles crossed into Poland on Friday during a "
     "huge barrage on Ukraine. Nobody was hurt. NATO's council meets in "
     "Brussels today; chief Mark Rutte called it a “grave violation”."),
    ("INDONESIA  •  DISASTER", "50 missing after candy factory fire",
     "A fire tore through the PT Fonusa Agung Mulia candy factory in Banten "
     "on Saturday evening. Three workers are confirmed dead, seven body "
     "bags were recovered and about 50 are missing."),
    ("JUSTICE  •  THE HAGUE", "World court: Myanmar committed genocide",
     "The International Court of Justice ruled on Thursday that Myanmar "
     "committed genocide against the Rohingya in 2017 — the first time it "
     "has found a state guilty of genocide. Reparations were ordered."),
    ("SPORT  •  TENNIS", "Alcaraz beats Zverev to win ATP Finals",
     "Carlos Alcaraz beat world No. 1 Alexander Zverev 6–2, 7–6(7) in Turin "
     "on Sunday to win his first ATP Finals title. He is only the fourth "
     "man to hold a career Grand Slam and this trophy."),
]
GX, GY = 32, 574
CW, CH, GAPX, GAPY = 306, 178, 12, 10
for i, (kicker, head, body) in enumerate(cards):
    x = GX + (i % 3) * (CW + GAPX)
    yy = GY + (i // 3) * (CH + GAPY)
    d.rounded_rectangle([x, yy, x + CW, yy + CH], radius=6, fill=CARD,
                        outline=RULE, width=1)
    d.text((x + 12, yy + 10), kicker, font=F(SANS_B, 13), fill=RED)
    hy = block(d, x + 12, yy + 32, head, F(SERIF_B, 19), CW - 24, 23, cap=2)
    block(d, x + 12, hy + 4, body, F(SANS, 13), CW - 24, 17, cap=5)

# ---------------- footer + ticker ----------------
d.text((32, 942),
       "Sources: Reuters, AP, CNN, BBC, AFP, ATP Tour  •  First reported 22–23 Nov 2026; markets are Friday's trading; ICJ ruling 19 Nov.",
       font=F(SANS, 12), fill=GREY)
d.rectangle([0, 962, W, H], fill=NAVY)
d.text((32, 968), "ALSO TODAY", font=F(SANS_B, 14), fill=GOLD)
d.text((32, 986),
       "Belgium grounds all flights 07:00–21:00 today in a national strike — 429 flights, 59,500 passengers  •  Nepal's PM meets Modi in Delhi",
       font=F(SANS, 13), fill=(235, 235, 240))
d.text((32, 1004),
       "South Korea's education minister quits over AI cheating  •  India post a record 720/9 in Wellington  •  Van Gogh sells for $190.4m in New York",
       font=F(SANS, 13), fill=(235, 235, 240))

img.save(OUT, "PNG", optimize=True)
print("saved", OUT, img.size)
