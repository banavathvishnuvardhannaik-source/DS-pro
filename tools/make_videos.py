#!/usr/bin/env python3
"""
MBU Data Science Lab — execution video generator.

For every experiment section in experiments_spec.py this script:
  1. EXECUTES the real Python code and captures stdout (+ plot PNG).
  2. Renders a 1280x720 "screen-recording style" video: editor window,
     syntax-highlighted code reveal, run animation, terminal with the
     REAL captured output typing in, optional plot card slide-in.
  3. Mixes a soft generated ambient music bed underneath.
  4. Regenerates js/data.js so the website always matches the videos.

Run:  python tools/make_videos.py
Requires: Pillow, numpy, pandas, imageio-ffmpeg, openpyxl, matplotlib, seaborn
"""

import json
import math
import os
import re
import subprocess
import sys
import wave
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg

sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiments_spec import EXPERIMENTS_SPEC

# ---------------- paths & constants ----------------
PROJECT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT / "assets" / "videos"
BUILD_DIR = PROJECT / "tools" / "build"
W, H = 1280, 720
FPS = 24
SECTION_DUR = 10.0
PREVIEW_DUR = 10.0

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

FONT_DIR = Path("C:/Windows/Fonts")
F_CODE = str(FONT_DIR / "consola.ttf")
F_CODE_B = str(FONT_DIR / "consolab.ttf")
F_TITLE = str(FONT_DIR / "arialbd.ttf")
F_TEXT = str(FONT_DIR / "arial.ttf")

# ---------------- video palette (matches new site theme) ----------------
BG_TOP = (22, 10, 16)
BG_BOT = (34, 16, 26)
WIN_BG = (30, 18, 28)
WIN_BAR = (43, 26, 40)
WIN_LINE = (66, 42, 58)
GUTTER_BG = (26, 15, 24)
GOLD = (201, 162, 39)
GOLD_SOFT = (228, 198, 110)
BURG = (140, 29, 64)
FG = (232, 223, 210)
MUTED = (146, 128, 138)
GREEN = (126, 211, 160)

TOK_COLORS = {
    "com": (122, 106, 116),
    "str": (165, 214, 167),
    "kw": (240, 113, 120),
    "num": (212, 175, 55),
    "fn": (121, 184, 255),
}

# ---------------- syntax highlighting ----------------
TOKEN_RE = re.compile(
    r"(?P<com>\#[^\n]*)"
    r"|(?P<str>\"\"\"[\s\S]*?\"\"\"|'''[\s\S]*?'''|\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*')"
    r"|(?P<kw>\b(?:import|from|as|def|return|if|elif|else|for|while|in|not|and|or|is|None|True|False|class|try|except|finally|with|lambda|pass|break|continue|print)\b)"
    r"|(?P<num>\b\d+(?:\.\d+)?\b)"
    r"|(?P<fn>\b[A-Za-z_]\w*(?=\s*\())"
)

def highlight_line(line):
    """Return list of (text, color) tokens for one source line."""
    out, last = [], 0
    for m in TOKEN_RE.finditer(line):
        if m.start() > last:
            out.append((line[last:m.start()], FG))
        kind = m.lastgroup
        out.append((m.group(), TOK_COLORS.get(kind, FG)))
        last = m.end()
    if last < len(line):
        out.append((line[last:], FG))
    return out or [("", FG)]

def wrap_text(text, width):
    lines = []
    for raw in text.split("\n"):
        line = raw.rstrip()
        while len(line) > width:
            lines.append(line[:width])
            line = line[width:]
        lines.append(line)
    return lines

# ---------------- easing helpers ----------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3

def ease_in_out(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

# ---------------- code execution ----------------
def execute_section(code, has_plot, workdir):
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    src = code
    if has_plot:
        src += (
            "\nimport matplotlib\nmatplotlib.use('Agg')\n"
            "import matplotlib.pyplot as plt\n"
            "plt.savefig('plot.png', dpi=150, bbox_inches='tight', facecolor='white')\n"
        )
    script = workdir / "script.py"
    script.write_text(src, encoding="utf-8")
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONWARNINGS"] = "ignore"
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=workdir, env=env, timeout=90,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        output = proc.stdout.strip("\n")
        if proc.returncode != 0:
            tail = proc.stderr.strip("\n").split("\n")
            output = (output + "\n" if output else "") + "\n".join(tail[-4:])
    except Exception as exc:  # timeout etc.
        output = f"(execution failed: {exc})"
    plot = workdir / "plot.png"
    return output, (str(plot) if has_plot and plot.exists() else None)

# ---------------- music ----------------
def make_music(path, dur=42.0, sr=44100):
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    out = np.zeros_like(t)
    chords = [
        [261.63, 329.63, 392.00, 493.88],   # Cmaj7
        [220.00, 261.63, 329.63, 392.00],   # Am7
        [174.61, 220.00, 261.63, 329.63],   # Fmaj7
        [196.00, 246.94, 293.66, 349.23],   # G7
    ]
    seg = 4.0
    for i in range(int(dur / seg) + 1):
        chord = chords[i % len(chords)]
        mask = (t >= i * seg) & (t < (i + 1) * seg)
        tt = t[mask] - i * seg
        env = np.clip(np.minimum(tt / 1.2, 1.0) * np.minimum((seg - tt) / 1.6, 1.0), 0, 1)
        for f in chord:
            out[mask] += env * np.sin(2 * np.pi * f * tt + 0.08 * np.sin(2 * np.pi * 0.4 * tt)) * 0.11
    # gentle pluck melody (C pentatonic)
    penta = [523.25, 587.33, 659.25, 783.99, 880.00]
    rng = np.random.default_rng(3)
    for k in range(int(dur * 2)):
        st = k * 0.5 + rng.uniform(-0.02, 0.02)
        f = penta[rng.integers(0, len(penta))] * (0.5 if rng.random() < 0.25 else 1.0)
        mask = (t >= st) & (t < st + 0.9)
        tt = t[mask] - st
        out[mask] += np.exp(-4.5 * tt) * np.sin(2 * np.pi * f * tt) * 0.09
    out = np.tanh(out * 1.2)
    out *= 0.55 / (np.max(np.abs(out)) + 1e-9)
    pcm = (out * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())

# ---------------- shared drawing assets (per-process cache) ----------------
_CACHE = {}

def fonts():
    if "fonts" not in _CACHE:
        _CACHE["fonts"] = {
            "code": ImageFont.truetype(F_CODE, 16),
            "code_sm": ImageFont.truetype(F_CODE, 15),
            "term": ImageFont.truetype(F_CODE, 15),
            "term_b": ImageFont.truetype(F_CODE_B, 15),
            "tab": ImageFont.truetype(F_CODE, 13),
            "title": ImageFont.truetype(F_TITLE, 54),
            "h2": ImageFont.truetype(F_TITLE, 30),
            "h3": ImageFont.truetype(F_TITLE, 22),
            "caps": ImageFont.truetype(F_TITLE, 15),
            "small": ImageFont.truetype(F_TEXT, 14),
            "chip": ImageFont.truetype(F_TITLE, 14),
        }
    return _CACHE["fonts"]

def base_bg():
    if "bg" not in _CACHE:
        yy = np.linspace(0, 1, H)[:, None]
        grad = np.zeros((H, W, 3), np.float32)
        for c in range(3):
            grad[..., c] = BG_TOP[c] + (BG_BOT[c] - BG_TOP[c]) * yy
        img = Image.fromarray(grad.astype(np.uint8), "RGB")
        d = ImageDraw.Draw(img)
        for x in range(0, W, 34):
            for y in range(0, H, 34):
                d.point((x, y), fill=(48, 28, 42))
        _CACHE["bg"] = img
    return _CACHE["bg"].copy()

def shadowed_panel(layer, box, radius, fill, outline=None, shadow=18):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(box, radius, fill=(0, 0, 0, 140))
    sh = sh.filter(ImageFilter.GaussianBlur(shadow))
    layer.alpha_composite(sh, (0, shadow // 2))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius, fill=fill, outline=outline, width=1 if outline else 0)
    return d

def draw_editor(d, box, filename):
    """Draw editor window chrome. Returns the title-bar height."""
    x0, y0, x1, y1 = box
    bar_h = 40
    # title bar
    d.rounded_rectangle(box, 14, fill=WIN_BAR)
    d.rectangle([x0, y0 + bar_h // 2, x1, y0 + bar_h], fill=WIN_BAR)
    for i, c in enumerate([(239, 95, 87), (246, 189, 46), (39, 201, 63)]):
        d.ellipse([x0 + 18 + i * 22, y0 + 14, x0 + 30 + i * 22, y0 + 26], fill=c)
    f = fonts()
    d.rounded_rectangle([x0 + 92, y0 + 7, x0 + 300, y0 + bar_h - 6], 7, fill=WIN_BG)
    d.text((x0 + 106, y0 + 12), filename, font=f["tab"], fill=GOLD_SOFT)
    d.ellipse([x0 + 282, y0 + 16, x0 + 290, y0 + 24], fill=BURG)
    d.text((x1 - 150, y0 + 12), "Python 3.11", font=f["tab"], fill=MUTED)
    # body
    d.rounded_rectangle([x0, y0 + bar_h, x1, y1], 14, fill=WIN_BG)
    d.rectangle([x0, y0 + bar_h, x1, y0 + bar_h + 14], fill=WIN_BG)
    d.line([x0, y0 + bar_h, x1, y0 + bar_h], fill=WIN_LINE)
    return bar_h

def code_block(d, layer, box, bar_h, code_tokens, t, job, font_key="code"):
    """Fast typewriter editor: code types in char-by-char with a blinking caret,
    the view scrolls to follow the typing, everything completes quickly."""
    x0, y0, x1, y1 = box
    f = fonts()
    font = f[font_key]
    lh = 25
    gutter = 58
    top = y0 + bar_h + 8
    bottom = y1 - 8
    visible = int((bottom - top) // lh)
    n = len(code_tokens)

    # ---- typing schedule (fast) ----
    start_t, type_end = 0.4, 5.0
    total_chars = job["total_chars"]
    chars = int(clamp((t - start_t) / (type_end - start_t)) * total_chars)
    chars = max(0, min(total_chars, chars))

    # ---- current line (for scroll follow + caret) ----
    acc = 0
    cur_line = 0
    for i in range(n):
        if chars > acc:
            cur_line = i
        acc += job["line_lens"][i]
    target_scroll = max(0, (cur_line - visible + 3)) * lh
    scroll = job.get("_scroll", 0.0) + (target_scroll - job.get("_scroll", 0.0)) * 0.3
    job["_scroll"] = scroll

    # gutter bg
    d.rectangle([x0, y0 + bar_h, x0 + gutter, y1], fill=GUTTER_BG)
    d.line([x0 + gutter, y0 + bar_h, x0 + gutter, y1], fill=WIN_LINE)

    content = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(content)
    remaining = chars
    caret = None
    for i in range(n):
        if remaining <= 0:
            break
        line_total = job["line_lens"][i]
        show = min(line_total, remaining)   # includes the '\n' pacing char
        remaining -= show
        ly = top + i * lh - scroll
        if top - lh <= ly <= bottom:
            cd.text((x0 + gutter - 12 - cd.textlength(str(i + 1), font=f["tab"]), ly + 3),
                    str(i + 1), font=f["tab"], fill=GOLD)
            tx = x0 + gutter + 14
            left = show
            for text, col in code_tokens[i]:
                if left <= 0:
                    break
                part = text[:left]
                if part:
                    cd.text((tx, ly), part, font=font, fill=col)
                    tx += cd.textlength(part, font=font)
                left -= len(text)
            caret = (tx, ly)
    # blinking caret while typing
    if caret and t < type_end + 0.3 and int(t * 3.5) % 2 == 0:
        cx, cy = caret
        cd.rectangle([cx + 1, cy + 2, cx + 9, cy + 19], fill=GOLD + (230,))

    mask = Image.new("L", layer.size, 0)
    ImageDraw.Draw(mask).rectangle([x0 + 2, top - 4, x1 - 2, bottom + 4], fill=255)
    layer.paste(content, (0, 0), mask)

def draw_terminal(d, box, appear_t, prompt, out_lines, type_t, font_key="term"):
    """Terminal panel; type_t in [0,1] = fraction of output typed."""
    x0, y0, x1, y1 = box
    f = fonts()
    bar_h = 34
    d.rounded_rectangle(box, 12, fill=(16, 10, 18), outline=WIN_LINE)
    d.rounded_rectangle([x0, y0, x1, y0 + bar_h], 12, fill=(26, 17, 26))
    d.rectangle([x0, y0 + bar_h // 2, x1, y0 + bar_h], fill=(26, 17, 26))
    d.ellipse([x0 + 14, y0 + 11, x0 + 24, y0 + 21], fill=(239, 95, 87))
    d.text((x0 + 38, y0 + 9), "TERMINAL — python output", font=f["tab"], fill=MUTED)
    lh = 20
    top = y0 + bar_h + 10
    bottom = y1 - 10
    visible = max(1, int((bottom - top) // lh))
    lines = [("prompt", prompt)] + [("out", l) for l in out_lines]
    total = len(lines)
    typed = int(ease_in_out(type_t) * total + 0.0001)
    typed = min(total, typed)
    start = max(0, typed - visible)
    for j in range(start, typed):
        kind, text = lines[j]
        ly = top + (j - start) * lh
        if kind == "prompt":
            d.text((x0 + 16, ly), text, font=f["term_b"], fill=GOLD)
        else:
            d.text((x0 + 16, ly), text, font=f["term"], fill=(216, 232, 210))
    # blinking caret
    if typed < total and int(type_t * 30) % 2 == 0 and typed > start:
        ly = top + (typed - start - 1) * lh
        last = lines[typed - 1][1]
        cx = x0 + 16 + d.textlength(last, font=f["term"]) + 4
        d.rectangle([cx, ly + 3, cx + 8, ly + 17], fill=GREEN + (200,))

def draw_player_chrome(d, t, dur):
    """Bottom video-player style progress bar + time, like a real video."""
    d.rectangle([0, H - 6, W, H], fill=(20, 12, 18))
    d.rectangle([0, H - 6, int(W * clamp(t / dur)), H], fill=GOLD)
    f = fonts()
    def fmt(s):
        return f"{int(s // 60)}:{int(s % 60):02d}"
    d.text((W - 132, H - 30), f"{fmt(t)} / {fmt(dur)}", font=f["tab"], fill=MUTED)
    d.text((24, H - 30), "MBU · Data Science Laboratory Management System", font=f["tab"], fill=(120, 100, 112))
    d.ellipse([W - 34, 20, W - 16, 38], outline=GOLD, width=2)
    d.text((W - 32, 17), "M", font=f["tab"], fill=GOLD_SOFT)

# ---------------- section video frames ----------------
def section_frame(t, job):
    dur = SECTION_DUR
    img = base_bg().convert("RGBA")
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    win = (40, 50, W - 40, 486)
    a = ease_out(t / 0.6)

    # editor
    shadowed_panel(layer, win, 14, WIN_BG + (int(255 * a),), WIN_LINE + (int(255 * a),))
    d = ImageDraw.Draw(layer)
    bar_h = draw_editor(d, win, job["filename"])
    code_block(d, layer, win, bar_h, job["code_tokens"], t, job)
    d = ImageDraw.Draw(layer)

    # running pill
    if 5.1 < t < 5.9:
        pulse = 0.65 + 0.35 * math.sin((t - 5.1) * 12)
        pw = 250
        px0, py0 = win[2] - pw - 16, win[3] - 48
        d.rounded_rectangle([px0, py0, px0 + pw, py0 + 32], 16,
                            fill=BURG + (int(235 * pulse),), outline=GOLD + (200,))
        d.polygon([(px0 + 16, py0 + 9), (px0 + 16, py0 + 23), (px0 + 27, py0 + 16)], fill=(255, 240, 210))
        d.text((px0 + 38, py0 + 8), f"Running {job['filename']} …", font=fonts()["tab"],
               fill=(255, 244, 220))

    # terminal
    term = (40, 508, W - 40, 688)
    ap = ease_out((t - 5.7) / 0.45)
    if ap > 0:
        off = int((1 - ap) * 46)
        tbox = (term[0], term[1] + off, term[2], term[3] + off)
        content = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_terminal(ImageDraw.Draw(content), tbox, ap, job["prompt"], job["out_lines"],
                      clamp((t - 6.1) / 3.0))
        mask = Image.new("L", img.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle(tbox, 12, fill=int(255 * ap))
        layer.paste(content, (0, 0), mask)
        d = ImageDraw.Draw(layer)

    # plot card
    if job.get("plot_img") is not None:
        pt = ease_out((t - 7.4) / 0.7)
        if pt > 0:
            card_w, card_h = 500, 330
            cx0 = W - 40 - card_w - 12
            cy1 = win[3] - 18
            cy0 = cy1 - card_h
            dy = int((1 - pt) * 60)
            card = Image.new("RGBA", (card_w + 60, card_h + 60), (0, 0, 0, 0))
            cd = ImageDraw.Draw(card)
            sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle([20, 20, 20 + card_w, 20 + card_h], 14, fill=(0, 0, 0, 160))
            sh = sh.filter(ImageFilter.GaussianBlur(14))
            card.alpha_composite(sh, (0, 6))
            cd.rounded_rectangle([20, 20, 20 + card_w, 20 + card_h], 14, fill=(255, 255, 255, 255))
            cd.rounded_rectangle([20, 20, 20 + card_w, 52], 14, fill=(247, 243, 234, 255))
            cd.rectangle([20, 40, 20 + card_w, 52], fill=(247, 243, 234, 255))
            cd.text((34, 28), "Figure 1 — plot output", font=fonts()["tab"], fill=(90, 70, 40))
            pw, ph = job["plot_img"].size
            scale = min((card_w - 36) / pw, (card_h - 70) / ph)
            pic = job["plot_img"].resize((int(pw * scale), int(ph * scale)), Image.LANCZOS)
            card.paste(pic, (20 + (card_w - pic.width) // 2, 58 + (card_h - 64 - pic.height) // 2),
                       pic if pic.mode == "RGBA" else None)
            tmp = Image.new("RGBA", img.size, (0, 0, 0, 0))
            tmp.alpha_composite(card, (cx0 - 20, cy0 - 20 + dy))
            if pt < 1:
                alpha = tmp.split()[3].point(lambda v: int(v * pt))
                tmp.putalpha(alpha)
            layer.alpha_composite(tmp)
            d = ImageDraw.Draw(layer)

    # section chip
    chip_t = ease_out((t - 0.3) / 0.5)
    if chip_t > 0:
        txt = f"Experiment {job['exp_number']} · Section {job['letter']} — {job['title']}"
        f = fonts()
        tw = d.textlength(txt, font=f["chip"])
        bx0, by0 = 40, 12
        d.rounded_rectangle([bx0, by0, bx0 + tw + 70, by0 + 30], 15,
                            fill=(24, 14, 22, int(230 * chip_t)), outline=GOLD + (int(200 * chip_t),))
        d.rounded_rectangle([bx0 + 8, by0 + 5, bx0 + 28, by0 + 25], 8, fill=BURG + (int(255 * chip_t),))
        d.text((bx0 + 13, by0 + 5), job["letter"], font=f["chip"], fill=(255, 244, 220, int(255 * chip_t)))
        d.text((bx0 + 38, by0 + 7), txt, font=f["chip"], fill=GOLD_SOFT + (int(255 * chip_t),))

    img.alpha_composite(layer)
    d = ImageDraw.Draw(img)
    draw_player_chrome(d, t, dur)

    # end fade
    fade = clamp((t - (dur - 0.55)) / 0.55)
    if fade > 0:
        overlay = Image.new("RGBA", img.size, (10, 5, 9, int(255 * ease_in_out(fade))))
        img.alpha_composite(overlay)
    return img.convert("RGB")

# ---------------- preview video frames ----------------
def preview_frame(t, job):
    dur = PREVIEW_DUR
    img = base_bg().convert("RGBA")
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = fonts()

    # ---------- scene 1: title card (0 - 2.6s) ----------
    if t < 3.0:
        k = ease_out(t / 0.8)
        cx = W // 2
        d.text((cx - d.textlength("MOHAN BABU UNIVERSITY", font=f["caps"]) / 2, 150),
               "MOHAN BABU UNIVERSITY", font=f["caps"], fill=GOLD + (int(255 * k),))
        d.text((cx - d.textlength("DATA SCIENCE LABORATORY", font=f["small"]) / 2, 178),
               "DATA SCIENCE LABORATORY", font=f["small"], fill=MUTED + (int(255 * k),))
        ttl = f"EXPERIMENT {job['exp_number']}"
        d.text((cx - d.textlength(ttl, font=f["caps"]) / 2, 262),
               ttl, font=f["caps"], fill=(240, 113, 120) + (int(255 * k),))
        name = job["name"]
        nf = f["title"]
        if d.textlength(name, font=nf) > W - 220:
            nf = f["h2"]
        k2 = ease_out((t - 0.35) / 0.8)
        d.text((cx - d.textlength(name, font=nf) / 2, 300), name, font=nf,
               fill=(245, 238, 226) + (int(255 * k2),))
        # gold underline sweep
        uw = min(d.textlength(name, font=nf) + 30, W - 260)
        ux0 = cx - uw / 2
        sweep = ease_in_out((t - 1.0) / 1.0)
        d.rounded_rectangle([ux0, 300 + nf.size + 18, ux0 + uw * sweep, 300 + nf.size + 23], 2,
                            fill=GOLD + (255,))
        # section chips
        chips = job["letters"]
        cw = 44
        total = len(chips) * cw + (len(chips) - 1) * 12
        x = cx - total / 2
        for i, L in enumerate(chips):
            ck = ease_out((t - 1.5 - i * 0.12) / 0.4)
            if ck <= 0:
                continue
            d.rounded_rectangle([x, 430, x + cw, 430 + 40], 10,
                                fill=WIN_BG + (int(255 * ck),), outline=GOLD + (int(220 * ck),))
            d.text((x + cw / 2 - d.textlength(L, font=f["h3"]) / 2, 436), L, font=f["h3"],
                   fill=GOLD_SOFT + (int(255 * ck),))
            x += cw + 12
        d.text((cx - d.textlength("10 second preview", font=f["small"]) / 2, 510),
               "10 second preview", font=f["small"], fill=MUTED + (int(200 * k),))
        a_out = 1 - ease_in_out((t - 2.55) / 0.45)
        if a_out < 1:
            dim = Image.new("RGBA", img.size, (14, 7, 12, int(255 * (1 - a_out))))
            layer.alpha_composite(dim)

    # ---------- scene 2: code + output montage (2.6 - 10.8) ----------
    if t >= 2.6 and t < 9.2:
        mt = t - 2.6
        win = (40, 44, 720, 700)
        shadowed_panel(layer, win, 14, WIN_BG + (255,), WIN_LINE + (255,))
        d = ImageDraw.Draw(layer)
        bar_h = draw_editor(d, win, f"experiment_{job['exp_number']}.py")
        # continuously scrolling code (clipped to the code region)
        tokens = job["all_tokens"]
        lh = 24
        top = win[1] + bar_h + 6
        scroll = mt * 52
        first = int(scroll // lh)
        vis = int((win[3] - top) // lh) + 2
        font = f["code_sm"]
        content = Image.new("RGBA", img.size, (0, 0, 0, 0))
        cd = ImageDraw.Draw(content)
        for i in range(first, min(len(tokens), first + vis)):
            ly = top + i * lh - scroll
            cd.text((win[0] + 16, ly + 3), str(i + 1), font=f["tab"], fill=(90, 72, 84))
            tx = win[0] + 58
            for text, col in tokens[i]:
                if not text:
                    continue
                if tx > win[2] - 20:
                    break
                cd.text((tx, ly), text, font=font, fill=col)
                tx += cd.textlength(text, font=font)
        cmask = Image.new("L", img.size, 0)
        ImageDraw.Draw(cmask).rectangle([win[0] + 2, top - 2, win[2] - 2, win[3] - 6], fill=255)
        layer.paste(content, (0, 0), cmask)
        d = ImageDraw.Draw(layer)
        # right terminal cycling section outputs
        term = (744, 44, W - 40, 700)
        shadowed_panel(layer, term, 14, (16, 10, 18, 255), WIN_LINE + (255,))
        d = ImageDraw.Draw(layer)
        d.text((term[0] + 18, term[1] + 12), "LIVE OUTPUT", font=f["caps"], fill=GOLD)
        slots = job["outputs"]            # list of (letter, [lines])
        per = 6.2 / max(1, len(slots))
        idx = min(len(slots) - 1, int(mt / per))
        local = (mt - idx * per) / per
        L, lines = slots[idx]
        # letter chip
        d.rounded_rectangle([term[0] + 18, term[1] + 44, term[0] + 58, term[1] + 84], 10, fill=BURG)
        d.text((term[0] + 31, term[1] + 50), L, font=f["h3"], fill=(255, 244, 220))
        d.text((term[0] + 72, term[1] + 56), f"Section {L} output", font=f["chip"], fill=GOLD_SOFT)
        max_lines = 24
        shown = int(ease_in_out(clamp(local * 1.25)) * min(len(lines), max_lines))
        for j in range(shown):
            d.text((term[0] + 18, term[1] + 108 + j * 20), lines[j], font=f["term"],
                   fill=(216, 232, 210))
        a_in = ease_out(mt / 0.45)
        a_out = 1 - ease_in_out((t - 8.85) / 0.45)
        cover = 1 - min(a_in, a_out)
        if cover > 0:
            dim = Image.new("RGBA", img.size, (14, 7, 12, int(255 * cover)))
            layer.alpha_composite(dim)

    # ---------- scene 3: outro (10.8 - 12.5) ----------
    if t >= 8.9:
        k = ease_out((t - 8.9) / 0.5)
        cx = W // 2
        msg = "Data Science Laboratory Management System"
        d.text((cx - d.textlength(msg, font=f["h2"]) / 2, 300), msg, font=f["h2"],
               fill=(245, 238, 226) + (int(255 * k),))
        sub = f"Experiment {job['exp_number']} · Sections {' · '.join(job['letters'])} · Mohan Babu University"
        d.text((cx - d.textlength(sub, font=f["small"]) / 2, 352), sub, font=f["small"],
               fill=GOLD_SOFT + (int(255 * k),))
        uw = 260 * ease_in_out((t - 9.2) / 0.6)
        d.rounded_rectangle([cx - uw / 2, 342, cx + uw / 2, 346], 2, fill=GOLD + (255,))

    img.alpha_composite(layer)
    d = ImageDraw.Draw(img)
    draw_player_chrome(d, t, dur)
    fade = clamp((t - (dur - 0.5)) / 0.5)
    if fade > 0:
        img.alpha_composite(Image.new("RGBA", img.size, (10, 5, 9, int(255 * ease_in_out(fade)))))
    return img.convert("RGB")

# ---------------- encoding ----------------
def encode(job):
    kind = job["kind"]
    dur = SECTION_DUR if kind == "section" else PREVIEW_DUR
    if job.get("plot"):
        job["plot_img"] = Image.open(job["plot"]).convert("RGB")
    n = int(dur * FPS)
    cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an",                                   # no sound
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "veryfast",
        "-movflags", "+faststart",
        "-t", f"{dur:.2f}", str(job["out"]),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    frame_fn = section_frame if kind == "section" else preview_frame
    for i in range(n):
        t = i / FPS
        frame = frame_fn(t, job)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()
    return job["out"]

def build_jobs(results):
    jobs = []
    for exp in EXPERIMENTS_SPEC:
        # ---- section jobs ----
        for sec in exp["sections"]:
            key = (exp["id"], sec["letter"])
            output, plot = results[key]
            out_lines = wrap_text(output, 120)[:26]
            code_lines = sec["code"].rstrip("\n").split("\n")
            tokens = [highlight_line(l) for l in code_lines]
            line_lens = [len(l) + 1 for l in code_lines]   # +1 = newline pacing
            jobs.append({
                "kind": "section",
                "exp_number": exp["number"],
                "letter": sec["letter"],
                "title": sec["title"],
                "filename": f"experiment_{exp['number']}{sec['letter'].lower()}.py",
                "prompt": f"PS C:\\MBU-DS-Lab> python experiment_{exp['number']}{sec['letter'].lower()}.py",
                "code_tokens": tokens,
                "line_lens": line_lens,
                "total_chars": sum(line_lens),
                "out_lines": out_lines,
                "plot": plot,
                "out": str(OUT_DIR / f"exp{exp['number']}-{sec['letter']}.mp4"),
            })
        # ---- preview job ----
        all_tokens = []
        outputs = []
        for sec in exp["sections"]:
            key = (exp["id"], sec["letter"])
            for l in sec["code"].rstrip("\n").split("\n"):
                all_tokens.append(highlight_line(l))
            all_tokens.append(highlight_line(f"# ---------- Section {sec['letter']} done ----------"))
            output, _ = results[key]
            outputs.append((sec["letter"], wrap_text(output, 56)[:24]))
        jobs.append({
            "kind": "preview",
            "exp_number": exp["number"],
            "name": exp["name"],
            "letters": [s["letter"] for s in exp["sections"]],
            "all_tokens": all_tokens,
            "outputs": outputs,
            "out": str(OUT_DIR / f"exp{exp['number']}-preview.mp4"),
        })
    return jobs

# ---------------- data.js regeneration ----------------
DATA_JS_TEMPLATE = '''/* ============================================================
   DATA FILE — EDIT EVERYTHING HERE
   ------------------------------------------------------------
   This file holds ALL editable content for the website:
     1. SITE        -> university / lab / subject code / logo
     2. STUDENT     -> ID card details (photo, name, id, ...)
     3. EXPERIMENTS -> experiments, sections, videos, code,
                       YouTube link, GitHub link, summary

   Sections are fully dynamic - an experiment may have any
   number of sections (A,B,C ... or A..H).

   Videos live in assets/videos/ and were generated by
   tools/make_videos.py from the REAL execution of this code.
   ============================================================ */

const SITE = {
  universityName: "Mohan Babu University",
  labName: "Data Science Laboratory Management System",
  subjectCode: "22AD3201",              // <- change the subject code here
  logoPath: "assets/mbu-logo.svg",      // <- replace with the real MBU logo
};

const STUDENT = {
  photo: "assets/student-photo.svg",    // <- replace with the student photo
  name: "Vishnu Vardhan",
  idNumber: "22101A0301",
  section: "CSE - A",
  faculty: "Dr. K. Faculty",
  profession: "B.Tech Student",
};

const EXPERIMENTS = %s;
'''

def write_data_js():
    experiments = []
    for exp in EXPERIMENTS_SPEC:
        experiments.append({
            "id": exp["id"],
            "number": exp["number"],
            "name": exp["name"],
            "previewVideo": f"assets/videos/exp{exp['number']}-preview.mp4",
            "youtubeVideo": exp["youtubeVideo"],
            "youtubeLink": exp["youtubeLink"],
            "githubLink": exp["githubLink"],
            "summary": exp["summary"],
            "sections": [
                {
                    "letter": s["letter"],
                    "title": s["title"],
                    "video": f"assets/videos/exp{exp['number']}-{s['letter']}.mp4",
                    "code": s["code"].rstrip("\n"),
                }
                for s in exp["sections"]
            ],
        })
    js = DATA_JS_TEMPLATE % json.dumps(experiments, indent=2, ensure_ascii=False)
    (PROJECT / "js" / "data.js").write_text(js, encoding="utf-8")
    print("  wrote js/data.js")

# ---------------- main ----------------
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    print("Executing all section code (real runs) …")
    results = {}
    for exp in EXPERIMENTS_SPEC:
        for sec in exp["sections"]:
            wd = BUILD_DIR / f"exp{exp['id']}{sec['letter']}"
            output, plot = execute_section(sec["code"], sec.get("plot", False), wd)
            results[(exp["id"], sec["letter"])] = (output, plot)
            first = output.split("\n")[0][:70] if output else "(no output)"
            print(f"  exp{exp['number']}{sec['letter']}: {'plot+ ' if plot else ''}{first}")

    jobs = build_jobs(results)
    # optional filter: python tools/make_videos.py exp1A exp5-preview
    filters = [a.lower() for a in sys.argv[1:]]
    if filters:
        def key(j):
            name = Path(j["out"]).stem.lower().replace("-", "")
            return any(f.replace("-", "") in name for f in filters)
        jobs = [j for j in jobs if key(j)]
    workers = min(6, os.cpu_count() or 4)
    print(f"Rendering {len(jobs)} videos on {workers} workers (no audio) …")
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for out in pool.map(encode, jobs):
            done += 1
            print(f"  [{done}/{len(jobs)}] {Path(out).name}")

    # write_data_js()  # skipped: data.js already updated manually
    print("All videos generated in assets/videos/")

if __name__ == "__main__":
    main()
