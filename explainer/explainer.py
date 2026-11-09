"""Reusable pieces for a narrated, 3Blue1Brown-style explainer video in Manim.

Copy this file next to the scene file and import from it:

    from explainer import Narrated, text, Landscape, curve, ACCENT, GOOD, BAD

Environment variables:
    VIDEO_VOICE_DIR   folder holding kokoro.onnx and voices.bin; without it the
                      video is silent and captioned.
    VIDEO_VOICE       Kokoro voice, default am_michael.
    VIDEO_LANG        Kokoro language code, default en-us.
    VIDEO_CAPTIONS    1 to force captions with a voice, 0 to hide them.
    VIDEO_FONT        font family of on-screen text, default Latin Modern Roman.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

import numpy as np
from manim import BLUE_C
from manim import DOWN
from manim import GREY_A
from manim import GREY_B
from manim import ORIGIN
from manim import RIGHT
from manim import UP
from manim import WHITE
from manim import FadeIn
from manim import FadeOut
from manim import ImageMobject
from manim import Line
from manim import Rectangle
from manim import Scene
from manim import Square
from manim import Text
from manim import VGroup
from manim import VMobject
from manim import config

config.background_color = "#0e1116"

FONT = os.environ.get("VIDEO_FONT", "Latin Modern Roman")
ACCENT = "#ff9a3c"  # the thing being looked at now
SOLVED = BLUE_C  # what is already known
GOOD = "#5fd38d"  # the best so far, a valid result
BAD = "#ff5c5c"  # a failure, a wrong claim
VOICE = os.environ.get("VIDEO_VOICE", "am_michael")
LANG = os.environ.get("VIDEO_LANG", "en-us")
CAPTIONS = os.environ.get(
    "VIDEO_CAPTIONS", "0" if os.environ.get("VIDEO_VOICE_DIR") else "1"
) not in {"0", ""}

# Rewritings of on-screen text that a speech synthesizer would misread. They
# apply in order, so put whole phrases first and single symbols last. Extend
# EXTRA_SPOKEN in the scene file for the paper's own notation.
SPOKEN = [
    (r"(\d)D\b", r"\1 D"),
    (r"\bf = ", "f equals "),
    (r" = ", " equals "),
    (r"−", "minus "),
    (r"≥", "at least"),
    (r"≤", "at most"),
    (r"≈", "about"),
    (r"×", " times "),
    (r"∇", "the gradient of "),
    (r"∈", "in"),
    (r"→", ","),
    (r"[—…;]", ","),
    (r"α", "alpha"),
    (r"β", "beta"),
    (r"γ", "gamma"),
    (r"δ", "delta"),
    (r"ε", "epsilon"),
    (r"θ", "theta"),
    (r"κ", "kappa"),
    (r"λ", "lambda"),
    (r"μ", "mu"),
    (r"σ", "sigma"),
    (r"π", "pi"),
    (r"\s+,", ","),
    (r",+", ","),
    (r"^\s*,\s*", ""),
]
EXTRA_SPOKEN: list[tuple[str, str]] = []


def spoken(message):
    """Return a sentence as it is to be read aloud."""
    for pattern, replacement in EXTRA_SPOKEN + SPOKEN:
        message = re.sub(pattern, replacement, message)
    return message


def speech(message):
    """Return the cached audio file of a sentence and its duration, or None.

    The sentence is synthesized by Kokoro when VIDEO_VOICE_DIR is set, and the
    file is kept in its cache folder, so a re-render costs nothing.
    """
    directory = os.environ.get("VIDEO_VOICE_DIR")
    if not directory:
        return None

    import soundfile

    directory = Path(directory)
    key = hashlib.sha1(f"{VOICE}:{LANG}:{message}".encode()).hexdigest()[:16]
    path = directory / "cache" / f"{key}.wav"
    if not path.exists():
        from kokoro_onnx import Kokoro

        if not hasattr(speech, "model"):
            speech.model = Kokoro(
                str(directory / "kokoro.onnx"), str(directory / "voices.bin")
            )
        samples, rate = speech.model.create(message, voice=VOICE, lang=LANG)
        path.parent.mkdir(parents=True, exist_ok=True)
        soundfile.write(path, samples, rate)

    return path, soundfile.info(path).duration


def text(string, size=32, color=WHITE, **kwargs):
    """Return on-screen text in the video's font."""
    return Text(string, font=FONT, font_size=size, color=color, **kwargs)


def curve(ax, xs, ys, **kwargs):
    """Return a polyline through sampled points, in the coordinates of axes."""
    return VMobject(**kwargs).set_points_as_corners([
        ax.c2p(x, y) for x, y in zip(xs, ys, strict=True)
    ])


def gif_frames(path, width=13.6):
    """Return the frames of a GIF as image mobjects, to play with add/remove."""
    from PIL import Image
    from PIL import ImageSequence

    with Image.open(path) as animation:
        frames = [
            ImageMobject(np.asarray(frame.convert("RGBA")))
            for frame in ImageSequence.Iterator(animation)
        ]
    for frame in frames:
        frame.scale_to_fit_width(width)
    return frames


class Narrated(Scene):
    """A scene whose sentences are read aloud, one after the other.

    narrate(sentence) starts a sentence as the next animation begins and
    returns at once, so the animations play under the voice; a new sentence
    first waits for the previous one to end, so voices never overlap. say()
    narrates and waits for the end, with a caption when captions are on.
    clear_all() waits for the voice before fading everything out, so no
    sentence is cut at the end of a scene.
    """

    caption = None
    voice_end = 0.0

    def hush(self):
        """Wait for the sentence being read to end."""
        remaining = self.voice_end - self.renderer.time
        if remaining > 0:
            self.wait(remaining + 0.2)

    def narrate(self, message):
        """Start reading a sentence once the previous one has ended."""
        audio = speech(spoken(message))
        if audio is None:
            return 0.0

        self.hush()
        self.add_sound(str(audio[0]))
        self.voice_end = self.renderer.time + audio[1]
        return audio[1]

    def say(self, message, wait=2.5, size=28, run_time=0.8, voice=None):
        """Read a sentence and wait for it, with a caption if captions are on."""
        duration = self.narrate(voice or message)
        if not CAPTIONS:
            self.wait(max(wait, duration + 0.4))
            return

        # Long enough to be read, about fifteen characters per second, or heard.
        wait = max(wait, 0.065 * len(message), duration - run_time + 0.6)
        words, lines = message.split(), [""]
        for w in words:
            if len(lines[-1]) + len(w) > 72:
                lines.append("")
            lines[-1] = (lines[-1] + " " + w).strip()
        new = text("\n".join(lines), size, color=GREY_A, line_spacing=0.8)
        if new.width > 13:
            new.scale_to_fit_width(13)
        new.to_edge(DOWN, buff=0.35)
        if self.caption is None:
            self.play(FadeIn(new, shift=0.15 * UP), run_time=run_time)
        else:
            self.play(
                FadeOut(self.caption, shift=0.15 * UP),
                FadeIn(new, shift=0.15 * UP),
                run_time=run_time,
            )
        self.caption = new
        self.wait(wait)

    def clear_all(self, run_time=0.8):
        """Wait for the voice, then fade out everything on screen."""
        self.hush()
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)
        self.caption = None


class Landscape:
    """A heat map of f(x, y) over a square, with helpers in its own coordinates."""

    def __init__(self, f, lo, hi, side=6.0, center=ORIGIN, res=500, cmap="magma", gamma=0.55):
        from matplotlib import colormaps

        xs = np.linspace(lo, hi, res)
        grid_x, grid_y = np.meshgrid(xs, xs[::-1])
        values = f(grid_x, grid_y)
        norm = ((values - values.min()) / (values.max() - values.min())) ** gamma
        rgba = colormaps[cmap](norm)
        rgba[:, :, :3] *= 0.85
        self.image = ImageMobject((rgba * 255).astype(np.uint8))
        self.image.height = side
        self.image.move_to(center)
        self.side, self.lo, self.hi = side, lo, hi
        self.frame = Square(side, color=GREY_B, stroke_width=2).move_to(center)

    def p(self, x, y):
        """Return the scene point of the data point (x, y)."""
        s = self.side / (self.hi - self.lo)
        c = self.frame.get_center()
        return c + ((x - self.lo) * s - self.side / 2) * RIGHT + (
            (y - self.lo) * s - self.side / 2
        ) * UP

    def grid(self, m, color=WHITE, opacity=0.85, width=1.6):
        """Return the lines cutting the square into m × m boxes."""
        lines = VGroup()
        for k in range(1, m):
            v = self.lo + k * (self.hi - self.lo) / m
            lines.add(Line(self.p(v, self.lo), self.p(v, self.hi), stroke_width=width, stroke_opacity=opacity, color=color))
            lines.add(Line(self.p(self.lo, v), self.p(self.hi, v), stroke_width=width, stroke_opacity=opacity, color=color))
        return lines

    def box(self, i, j, m=10, **kwargs):
        """Return box (i, j) of an m × m grid, i along x and j along y."""
        w = (self.hi - self.lo) / m
        a = self.p(self.lo + i * w, self.lo + j * w)
        b = self.p(self.lo + (i + 1) * w, self.lo + (j + 1) * w)
        return Rectangle(width=b[0] - a[0], height=b[1] - a[1], **kwargs).move_to((a + b) / 2)
