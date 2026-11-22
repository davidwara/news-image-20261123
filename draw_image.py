#!/usr/bin/env python3
"""One-page newspaper of world news for Monday 23 November 2026.

The page is drawn with Pillow at 1024x1024 and saved as entry.png.
Sections, top to bottom: a masthead with the date and a red top rule;
a lead story on the COP31 collapse with a two-column explainer and a
verdict strip; a dark band charting Friday's market rout; six story
cards in two rows of three; and a navy ticker footer.
The drawing is fully deterministic: fixed fonts, fixed geometry, no
clock, no randomness, no network. Running the script twice produces
byte-identical PNG output.

Every story below was verified against wire reporting on 23 Nov 2026
(Reuters, AP, CNN, BBC, AFP, ATP Tour). Dates are labelled in the
image wherever a story broke on an earlier day but led the news on
the 23rd: the COP31 collapse and the Dymer strike are Sunday's, the
market rout is Friday's, the ICJ ruling is Thursday's.
"""
from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 1024, 1024
OUTPUT_FILE = "entry.png"

FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

COL_INK = (20, 20, 22)
COL_PAGE = (251, 249, 244)
COL_RED = (176, 32, 26)
COL_NAVY = (15, 40, 88)
COL_SLATE = (22, 26, 36)
COL_GREY = (96, 96, 100)
COL_HAIRLINE = (178, 172, 162)
COL_CARD = (255, 255, 255)
COL_TEAL = (13, 104, 90)
COL_GOLD = (255, 208, 88)
COL_BAR = (255, 106, 96)
COL_MIST = (206, 206, 212)


def typeface(path, size):
    """Load a TrueType font at the requested point size."""
    return ImageFont.truetype(path, size)


def fit_lines(cv, text, face, max_width):
    """Greedy word wrap: split text into lines that fit max_width."""
    fitted, current = [], ""
    for word in text.split():
        attempt = (current + " " + word).strip()
        if cv.textlength(attempt, font=face) <= max_width:
            current = attempt
        else:
            if current:
                fitted.append(current)
            current = word
    if current:
        fitted.append(current)
    return fitted


def draw_para(cv, x, y, text, face, max_width, leading, fill=COL_INK, cap=None):
    """Draw wrapped text starting at (x, y); return the y below it."""
    lines = fit_lines(cv, text, face, max_width)
    if cap is not None:
        lines = lines[:cap]
    for line in lines:
        cv.text((x, y), line, font=face, fill=fill)
        y += leading
    return y


def hrule(cv, x0, x1, y, fill=COL_INK, width=2):
    """Draw a horizontal rule between x0 and x1 at height y."""
    cv.line([(x0, y), (x1, y)], fill=fill, width=width)


def drop_bar(cv, x_label, y, name, value, magnitude, x_bar, max_bar_width):
    """One row of the market chart: label, red bar, value."""
    cv.text((x_label, y), name, font=typeface(FONT_SANS_BOLD, 12), fill=COL_MIST)
    bar_width = int(max_bar_width * magnitude / 6.2)
    cv.rectangle([x_bar, y + 1, x_bar + bar_width, y + 12], fill=COL_BAR)
    cv.text((x_bar + bar_width + 6, y), value,
            font=typeface(FONT_SANS_BOLD, 12), fill=(255, 255, 255))


def story_card(cv, x, y, width, height, kicker, headline, body):
    """One white story card with a red kicker, serif headline, body."""
    cv.rounded_rectangle([x, y, x + width, y + height], radius=6,
                         fill=COL_CARD, outline=COL_HAIRLINE, width=1)
    cv.text((x + 12, y + 10), kicker, font=typeface(FONT_SANS_BOLD, 13), fill=COL_RED)
    after_head = draw_para(cv, x + 12, y + 32, headline,
                           typeface(FONT_SERIF_BOLD, 19), width - 24, 23, cap=2)
    draw_para(cv, x + 12, after_head + 4, body,
              typeface(FONT_SANS, 13), width - 24, 17, cap=5)


def build_page():
    """Compose the whole front page and return the Pillow image."""
    page = Image.new("RGB", (CANVAS_W, CANVAS_H), COL_PAGE)
    cv = ImageDraw.Draw(page)

    # ---------- masthead ----------
    cv.rectangle([0, 0, CANVAS_W, 10], fill=COL_RED)
    cv.text((32, 24), "THE WORLD IN ONE PAGE",
            font=typeface(FONT_SERIF_BOLD, 50), fill=COL_INK)
    cv.text((32, 84), "MONDAY, 23 NOVEMBER 2026",
            font=typeface(FONT_SANS_BOLD, 24), fill=COL_RED)
    cv.text((32, 116),
            "14 stories from one day  •  Antalya  •  Hormuz  •  Kyiv  •  The Hague  •  Turin",
            font=typeface(FONT_SANS, 17), fill=COL_GREY)
    cv.text((CANVAS_W - 32, 84), "No. 23",
            font=typeface(FONT_SERIF_BOLD, 24), fill=COL_INK, anchor="ra")
    cv.text((CANVAS_W - 32, 116), "MONDAY EDITION",
            font=typeface(FONT_SANS, 15), fill=COL_GREY, anchor="ra")
    hrule(cv, 32, CANVAS_W - 32, 146, fill=COL_INK, width=3)
    hrule(cv, 32, CANVAS_W - 32, 152, fill=COL_INK, width=1)

    # ---------- lead story: COP31 collapse ----------
    lead_y = 164
    cv.text((32, lead_y), "CLIMATE  •  THE LEAD STORY",
            font=typeface(FONT_SANS_BOLD, 17), fill=COL_TEAL)
    y = draw_para(cv, 32, lead_y + 26,
                  "COP31 COLLAPSES IN ANTALYA — NO CLIMATE DEAL",
                  typeface(FONT_SERIF_BOLD, 30), 960, 36, cap=2)
    y += 4
    cv.text((32, y),
            "The longest summit in history ends without a pact — the first major breakdown since Copenhagen in 2009.",
            font=typeface(FONT_SANS, 17), fill=COL_GREY)
    y += 24
    columns_y = y
    cv.text((32, columns_y), "WHAT HAPPENED",
            font=typeface(FONT_SANS_BOLD, 15), fill=COL_TEAL)
    draw_para(cv, 32, columns_y + 24,
              "After two days of overtime, COP31 presidents put the “Antalya Pact” "
              "to nearly 200 nations on Sunday — and the EU, Britain, Panama and "
              "others rejected it, because it never named fossil fuels. A $120bn "
              "finance target was dropped too.",
              typeface(FONT_SANS, 17), 590, 22, cap=4)
    cv.line([(652, columns_y), (652, columns_y + 128)], fill=COL_HAIRLINE, width=1)
    cv.text((672, columns_y), "THE GULF  •  WAR",
            font=typeface(FONT_SANS_BOLD, 15), fill=COL_RED)
    draw_para(cv, 672, columns_y + 24,
              "Iran's war with the U.S. and Israel, now in its ninth month, still "
              "rages around the Strait of Hormuz. Houthi missiles fired at Saudi "
              "Arabia were intercepted; Qatar-mediated talks have stalled.",
              typeface(FONT_SANS, 15), 320, 20, cap=5)
    verdict_y = columns_y + 132
    cv.rectangle([32, verdict_y, CANVAS_W - 32, verdict_y + 30],
                 outline=COL_RED, width=2)
    cv.text((44, verdict_y + 7),
            "VERDICT IN ANTALYA:  44 HOURS OF OVERTIME  •  NO CONSENSUS  •  PARIS DEAL STILL STANDS",
            font=typeface(FONT_SANS_BOLD, 14), fill=COL_RED)
    hrule(cv, 32, CANVAS_W - 32, 462, fill=COL_INK, width=2)

    # ---------- markets band: Friday's rout ----------
    cv.rectangle([0, 472, CANVAS_W, 566], fill=COL_SLATE)
    cv.text((32, 482), "FRIDAY'S ROUT: THE AI TRADE UNRAVELS",
            font=typeface(FONT_SANS_BOLD, 20), fill=(255, 255, 255))
    cv.text((32, 508), "The S&P 500 fell 3.7% on Friday, its worst week since March 2020.",
            font=typeface(FONT_SANS, 15), fill=COL_MIST)
    cv.text((32, 527), "Nasdaq 100 is in a bear market; world stocks fell 7 days in a row.",
            font=typeface(FONT_SANS, 15), fill=COL_MIST)
    cv.text((32, 546), "Tokyo is closed today for a holiday. Bitcoin near $59,900.",
            font=typeface(FONT_SANS, 15), fill=COL_MIST)
    friday_drops = [("TAIWAN", "-6.2%", 6.2),
                    ("NASDAQ", "-5.3%", 5.3),
                    ("KOSPI", "-5.2%", 5.2),
                    ("NIKKEI", "-5.1%", 5.1),
                    ("S&P 500", "-3.7%", 3.7)]
    for row, (name, value, magnitude) in enumerate(friday_drops):
        drop_bar(cv, 560, 480 + row * 17, name, value, magnitude, 640, 200)

    # ---------- story cards: two rows of three ----------
    stories = [
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
    grid_x, grid_y = 32, 574
    card_w, card_h, gap_x, gap_y = 306, 178, 12, 10
    for pos, (kicker, headline, body) in enumerate(stories):
        x = grid_x + (pos % 3) * (card_w + gap_x)
        y = grid_y + (pos // 3) * (card_h + gap_y)
        story_card(cv, x, y, card_w, card_h, kicker, headline, body)

    # ---------- footer: sources + ticker ----------
    cv.text((32, 942),
            "Sources: Reuters, AP, CNN, BBC, AFP, ATP Tour  •  First reported 22–23 Nov 2026; markets are Friday's trading; ICJ ruling 19 Nov.",
            font=typeface(FONT_SANS, 12), fill=COL_GREY)
    cv.rectangle([0, 962, CANVAS_W, CANVAS_H], fill=COL_NAVY)
    cv.text((32, 968), "ALSO TODAY",
            font=typeface(FONT_SANS_BOLD, 14), fill=COL_GOLD)
    cv.text((32, 986),
            "Belgium grounds all flights 07:00–21:00 today in a national strike — 429 flights, 59,500 passengers  •  Nepal's PM meets Modi in Delhi",
            font=typeface(FONT_SANS, 13), fill=(235, 235, 240))
    cv.text((32, 1004),
            "South Korea's education minister quits over AI cheating  •  India post a record 720/9 in Wellington  •  Van Gogh sells for $190.4m in New York",
            font=typeface(FONT_SANS, 13), fill=(235, 235, 240))
    return page


if __name__ == "__main__":
    front_page = build_page()
    front_page.save(OUTPUT_FILE, "PNG", optimize=True)
    print("saved", OUTPUT_FILE, front_page.size)
