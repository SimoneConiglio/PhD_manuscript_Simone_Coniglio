"""Narrated explainer of the thesis "Propulsion Airframe Topology Optimization including
engine performance and stress criteria" (S. Coniglio), following script.md.

Built with the paper-to-explainer-video skill
(https://github.com/SimoneConiglio/video-explaination-skill). To re-render:

    python precompute.py /path/to/GGP-Python            # once: data/*.npz
    export VIDEO_VOICE_DIR=/path/to/voice               # Kokoro model; omit for captions
    python synth.py                                     # synthesize every sentence once
    bash <skill>/scripts/render.sh <venv> video.py out qh
    bash <skill>/scripts/assemble.sh out qh explainer.mp4

Toy examples (ring, springs, two bars) are computed here; replayed runs come from data/.
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np
from explainer import ACCENT, BAD, EXTRA_SPOKEN, GOOD, SOLVED, Narrated, text
from manim import *  # noqa: F401,F403

DATA = HERE / "data"
ASSETS = HERE / "assets"
THESIS = HERE.parent / "Phd_SC" / "images"
MAT = np.array([88, 196, 221])
BGC = np.array([14, 17, 22])
NELX, NELY = 60, 30

EXTRA_SPOKEN += [
    (r"delta TSFC", "delta T S F C"),
    (r"TSFC", "T S F C"),
    (r"\bGGP\b", "G G P"),
    (r"\bMMC\b", "M M C"),
    (r"\bMNA\b", "M N A"),
    (r"\bKS\b", "K S"),
    (r"\bSIMP\b", "simp"),
]


# ------------------------------------------------------------------ helpers
def card(name, height=None, width=None):
    """A white-background figure from the thesis on a rounded card."""
    img = ImageMobject(str(ASSETS / f"{name}.png"))
    if height:
        img.height = height
    if width:
        img.width = width
    bg = RoundedRectangle(corner_radius=0.12, width=img.width + 0.24, height=img.height + 0.24,
                          fill_color=WHITE, fill_opacity=1, stroke_width=0)
    return Group(bg, img)


def field(values, nelx, nely, width, color=MAT):
    """A density field (top88 element order) as a crisp image."""
    a = np.clip(np.asarray(values).reshape(nelx, nely).T, 0, 1)[..., None]
    rgb = (BGC + (np.array(color) - BGC) * a).astype(np.uint8)
    rgba = np.concatenate([rgb, np.full((*rgb.shape[:2], 1), 255, np.uint8)], 2)
    rgba = np.repeat(np.repeat(rgba, 6, 0), 6, 1)
    img = ImageMobject(rgba)
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    img.width = width
    return img


def clamp_marks(rect, n=9):
    return VGroup(*[Line(rect.get_corner(UL) + DOWN * k * rect.height / (n - 1),
                         rect.get_corner(UL) + DOWN * k * rect.height / (n - 1) + 0.22 * LEFT + 0.15 * DOWN,
                         color=GREY_B, stroke_width=2) for k in range(n)])


def heading(s, size=40):
    return text(s, size).to_edge(UP, buff=0.4)


def number(v, decimals=0, size=40, color=WHITE):
    return DecimalNumber(v, num_decimal_places=decimals, group_with_commas=True,
                         font_size=size, color=color)


PARETO = None


def pareto():
    """(V %, delta TSFC %) of solutions A-D, from the thesis' pareto.mat (App. B)."""
    global PARETO
    if PARETO is None:
        from scipy.io import loadmat
        m = loadmat(str(THESIS / "Ch2" / "pareto.mat"))
        PARETO = {k: (float(m[f"V{t}"].squeeze()), float(m[f"T{t}"].squeeze())) for k, t in
                  (("A", "16"), ("B", "17"), ("C", "18"), ("D", "f"))}
    return PARETO


# ================================================================== 1. Hook
class S01Hook(Narrated):
    def construct(self):
        P = pareto()
        d = card("sol_d", height=3.0).move_to(3.4 * LEFT + 0.6 * UP)
        a = card("sol_a", height=3.0).move_to(3.4 * RIGHT + 0.6 * UP)
        self.narrate("Here are two designs for the structure that hangs a jet engine under a wing.")
        self.play(FadeIn(d, shift=UP * 0.2), FadeIn(a, shift=UP * 0.2), run_time=1.5)
        ok = VGroup(*[VGroup(MathTex(r"\checkmark", color=GOOD), text("same loads, no failure", 24, GREY_A)).arrange(RIGHT)
                      .next_to(c, DOWN, buff=0.25) for c in (d, a)])
        self.narrate("Both carry the same flight loads, and neither breaks.")
        self.play(LaggedStart(*[FadeIn(o) for o in ok], lag_ratio=0.4))
        vd, td = P["D"]
        va, ta = P["A"]
        nd = VGroup(text(f"volume {vd:.1f} %", 30), text(f"extra fuel {td:.3f} %", 30, BAD)).arrange(DOWN).next_to(ok[0], DOWN, buff=0.3)
        na = VGroup(text(f"volume {va:.1f} %", 30), text(f"extra fuel {ta:.3f} %", 30, GOOD)).arrange(DOWN).next_to(ok[1], DOWN, buff=0.3)
        self.narrate("The one on the left uses three point six percent of the available volume. During manoeuvres, "
                     "it lets the engine burn zero point one eight three percent more fuel.")
        self.play(FadeIn(nd[0]))
        self.play(FadeIn(nd[1]))
        self.narrate("The one on the right uses about a third more material, four point nine percent, and brings that "
                     "over-consumption down to zero point one six.")
        self.play(FadeIn(na[0]))
        self.play(FadeIn(na[1]))
        self.hush()
        self.play(*[FadeOut(m) for m in (ok, nd, na)], d.animate.scale(0.6).to_corner(UL, buff=0.4),
                  a.animate.scale(0.6).to_corner(UR, buff=0.4))
        ax = Axes(x_range=[3.4, 5.2, 0.4], y_range=[0.155, 0.19, 0.01], x_length=6, y_length=3.6,
                  axis_config={"color": GREY_B, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": [3.6, 4.0, 4.4, 4.8], "decimal_number_config": {"num_decimal_places": 1}},
                  y_axis_config={"numbers_to_include": [0.16, 0.17, 0.18], "decimal_number_config": {"num_decimal_places": 2}}
                  ).shift(0.9 * DOWN)
        xl = text("volume of material (%)", 22, GREY_A).next_to(ax.x_axis, DOWN, buff=0.45)
        yl = text("extra fuel in manoeuvres (%)", 22, GREY_A).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.55)
        pd = Dot(ax.c2p(vd, td), color=BAD, radius=0.1)
        pa = Dot(ax.c2p(va, ta), color=GOOD, radius=0.1)
        self.narrate("Same engine, same loads. The only difference is where the material sits.")
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        self.play(FadeIn(pd, scale=2), FadeIn(pa, scale=2))
        self.play(Create(DashedLine(pd.get_center(), pa.get_center(), color=GREY_B)))
        q = text("Where should it go?  And how would you find out?", 34, ACCENT).to_edge(DOWN, buff=0.3)
        self.narrate("So where should it go? And how would you even find out? That's what this thesis builds.")
        self.play(Write(q), run_time=2)
        self.clear_all()


# ================================================================== 2. Tip clearance
class S02Clearance(Narrated):
    def construct(self):
        c = 3.2 * LEFT + 0.2 * DOWN
        R, r = 2.6, 2.3
        t = ValueTracker(0)

        def casing():
            s = t.get_value()
            return ParametricFunction(lambda a: c + np.array([(R + 0.10 * s) * np.cos(a), (R - 0.10 * s) * np.sin(a) - 0.22 * s, 0]),
                                      t_range=[0, TAU], color=GREY_A, stroke_width=7)

        cas = always_redraw(casing)
        hub = Circle(0.55, color=SOLVED, fill_opacity=0.5).move_to(c)
        blades = VGroup(*[Line(c + 0.55 * np.array([np.cos(a), np.sin(a), 0]), c + r * np.array([np.cos(a), np.sin(a), 0]),
                               color=SOLVED, stroke_width=4) for a in np.linspace(0, TAU, 28, endpoint=False)])
        rotor = VGroup(hub, blades)
        spin = lambda m, dt: m.rotate(1.2 * dt, about_point=hub.get_center())
        self.narrate("Inside the engine, rows of blades spin a hair's breadth from a fixed casing.")
        self.play(Create(cas), FadeIn(rotor), run_time=1.5)
        rotor.add_updater(spin)
        self.wait(1)
        br = BraceBetweenPoints(c + UP * r, c + UP * R, RIGHT, color=ACCENT)
        bl = text("tip clearance", 30, ACCENT).next_to(br, RIGHT)
        self.narrate("That gap is called the tip clearance.")
        self.play(GrowFromCenter(br), FadeIn(bl))
        self.hush()
        self.play(FadeOut(br), FadeOut(bl))
        load = Arrow(c + 4.0 * UP + 0.8 * RIGHT, c + 2.9 * UP + 0.8 * RIGHT, color=BAD, buff=0)
        ll = text("manoeuvre load", 26, BAD).next_to(load, RIGHT)
        self.narrate("When the aircraft pulls a manoeuvre, the engine bends. The casing and the rotor move by different "
                     "amounts, so the gap opens here and closes there.")
        self.play(GrowArrow(load), FadeIn(ll))
        self.play(t.animate.set_value(1), rotor.animate.shift(0.07 * DOWN), run_time=2.5)
        top = Dot(c + UP * (R - 0.32), color=ACCENT)
        bot = Dot(c + DOWN * (R + 0.05), color=BAD, radius=0.12)
        lt = text("opens: air leaks", 26, ACCENT).move_to(1.6 * RIGHT + 2.2 * UP)
        lb = text("closes: blades rub", 26, BAD).move_to(1.6 * RIGHT + 2.6 * DOWN)
        self.narrate("Where it closes, the blades rub and wear the casing; where it opens, air leaks past the blade tips.")
        self.play(FadeIn(bot, scale=2), Flash(bot, color=BAD), FadeIn(lb))
        self.play(FadeIn(top), FadeIn(lt), Create(Arrow(lt.get_left(), top.get_center(), buff=0.15, color=ACCENT)),
                  Create(Arrow(lb.get_left(), bot.get_center(), buff=0.15, color=BAD)))
        res = VGroup(text("the stage works less well", 30), text("more fuel for the same thrust", 32, ACCENT)).arrange(DOWN, aligned_edge=LEFT).move_to(3.2 * RIGHT + 0.2 * DOWN)
        self.narrate("Either way, the stage works less well, and the engine burns more fuel for the same thrust.")
        self.play(FadeIn(res[0], shift=RIGHT * 0.2))
        self.play(FadeIn(res[1], shift=RIGHT * 0.2))
        self.hush()
        rotor.clear_updaters()
        self.clear_all()


# ================================================================== 3. Ring to one number (toy)
class S03Number(Narrated):
    def construct(self):
        n = 24
        th = np.linspace(0, TAU, n, endpoint=False)
        # toy displacements in mm (illustration): casing drops 0.12 and ovalizes, rotor drops 0.04
        uc = np.stack([0.06 * np.cos(2 * th) * np.cos(th), -0.12 + 0.06 * np.cos(2 * th) * np.sin(th)], 1)
        ub = np.stack([0 * th, -0.04 + 0 * th], 1)
        rad = np.stack([np.cos(th), np.sin(th)], 1)
        delta = ((uc - ub) * rad).sum(1)
        Rms = float(np.sqrt(np.mean(delta ** 2)))
        blade = 50.0
        dtsfc = Rms / blade * 100
        c = 4.3 * LEFT + 0.3 * DOWN
        R0, sc = 2.0, 6.0
        ring = Circle(R0, color=GREY_B, stroke_width=3).move_to(c)
        dots = VGroup(*[Dot(c + R0 * np.array([*rad[k], 0]), radius=0.045, color=GREY_A) for k in range(n)])
        hd = heading("Turning a bent ring into one number")
        self.narrate("To optimize something, we need a number. The thesis builds it in three steps.")
        self.play(Write(hd), Create(ring), FadeIn(dots))
        note = text("toy displacements, for illustration", 20, GREY_B).next_to(ring, DOWN, buff=0.3)
        self.play(FadeIn(note))
        ac = VGroup(*[Arrow(dots[k].get_center(), dots[k].get_center() + sc * np.array([*uc[k], 0]), buff=0,
                            color=GREY_A, stroke_width=3, max_tip_length_to_length_ratio=0.35) for k in range(n)])
        ab = VGroup(*[Arrow(dots[k].get_center(), dots[k].get_center() + sc * np.array([*ub[k], 0]), buff=0,
                            color=SOLVED, stroke_width=3, max_tip_length_to_length_ratio=0.35) for k in range(n)])
        s1 = text("1. clearance change at each angle", 26, ACCENT).move_to(2.4 * RIGHT + 2.4 * UP)
        f1 = MathTex(r"\delta(\theta)=\vec r(\theta)\cdot\big(\vec u_{casing}-\vec u_{rotor}\big)", font_size=34).next_to(s1, DOWN)
        self.narrate("First, at each angle, project the casing and rotor displacements on the radius. Their difference "
                     "is the change in clearance.")
        self.play(FadeIn(s1), LaggedStart(*[GrowArrow(x) for x in ac], lag_ratio=0.03), run_time=1.5)
        self.play(LaggedStart(*[GrowArrow(x) for x in ab], lag_ratio=0.03), Write(f1), run_time=1.5)
        ax = Axes(x_range=[0, TAU, PI / 2], y_range=[-0.16, 0.16, 0.08], x_length=5.2, y_length=2.0,
                  axis_config={"color": GREY_B, "include_tip": False}).move_to(2.6 * RIGHT + 0.25 * DOWN)
        ax_l = MathTex(r"\delta", font_size=30).next_to(ax.y_axis, LEFT)
        ax_t = MathTex(r"\theta", font_size=30).next_to(ax.x_axis, RIGHT, buff=0.1)
        bars = VGroup(*[Line(ax.c2p(th[k], 0), ax.c2p(th[k], delta[k]), stroke_width=7,
                             color=BAD if delta[k] < 0 else ACCENT) for k in range(n)])
        self.play(FadeOut(ac), FadeOut(ab), Create(ax), FadeIn(ax_l), FadeIn(ax_t))
        self.play(LaggedStart(*[Create(b) for b in bars], lag_ratio=0.04), run_time=1.5)
        s2 = text("2. root mean square: one number per stage", 26, ACCENT).move_to(2.4 * RIGHT + 1.85 * DOWN)
        f2 = MathTex(r"R=\sqrt{\tfrac{1}{N}\textstyle\sum_k \delta_k^2}=" + f"{Rms:.4f}" + r"\,\mathrm{mm}", font_size=34).next_to(s2, DOWN)
        self.narrate("Second, take the root mean square of these changes around the ring. One stage, one number.")
        self.play(FadeIn(s2))
        self.play(*[b.animate.put_start_and_end_on(ax.c2p(th[k], 0), ax.c2p(th[k], Rms + 1e-4)).set_color(GOOD)
                    for k, b in enumerate(bars)], Write(f2), run_time=2)
        self.hush()
        self.play(*[FadeOut(m) for m in (s1, f1, ax, ax_l, ax_t, bars, s2)], f2.animate.move_to(2.4 * RIGHT + 2.3 * UP))
        f3 = MathTex(r"\Delta\mathrm{TSFC}\,\%=\sum_{s}\frac{R_s}{l_s}\,100", font_size=40).next_to(f2, DOWN, buff=0.5)
        f3b = MathTex(r"\frac{" + f"{Rms:.4f}" + r"}{" + f"{blade:.0f}" + r"}\,100=" + f"{dtsfc:.3f}" + r"\,\%", font_size=34, color=ACCENT).next_to(f3, DOWN)
        lab = text("(this stage, blade height 50 mm)", 20, GREY_B).next_to(f3b, DOWN, buff=0.15)
        self.narrate("Third, divide by the blade height and add the stages up. That's the change in thrust specific "
                     "fuel consumption, delta TSFC, in percent.")
        self.play(Write(f3))
        self.play(FadeIn(f3b), FadeIn(lab))
        vals = [0.6 * dtsfc, dtsfc, 0.8 * dtsfc]
        bx = Axes(x_range=[0, 3, 1], y_range=[0, 0.16, 0.04], x_length=3.4, y_length=1.8,
                  axis_config={"color": GREY_B, "include_tip": False}).move_to(2.4 * RIGHT + 2.3 * DOWN)
        cols = VGroup(*[Rectangle(width=0.6, height=bx.c2p(0, v)[1] - bx.c2p(0, 0)[1], fill_color=SOLVED, fill_opacity=0.8, stroke_width=0)
                        .move_to(bx.c2p(k + 0.5, v / 2)) for k, v in enumerate(vals)])
        names = VGroup(*[MathTex(s, font_size=28).next_to(bx.c2p(k + 0.5, 0), DOWN) for k, s in enumerate(("F_x", "F_y", "F_z"))])
        self.narrate("And because the cold clearance must be set so the blades never rub in the worst case, it's the "
                     "worst manoeuvre that matters: with several load cases, we keep the largest.")
        self.play(Create(bx), FadeIn(names), LaggedStart(*[GrowFromEdge(cl, DOWN) for cl in cols], lag_ratio=0.3))
        self.play(cols[1].animate.set_color(ACCENT), Indicate(cols[1], color=ACCENT))
        sm = text("every step: linear or smooth in the displacements", 26, GOOD).to_edge(DOWN, buff=0.3)
        self.narrate("Notice that every step is linear or smooth in the displacements. That will matter.")
        self.play(FadeIn(sm, shift=UP * 0.2))
        self.clear_all()


# ================================================================== 4. The design problem
class S04Problem(Narrated):
    def construct(self):
        fem = card("fem_intro", height=5.2).move_to(3.3 * LEFT + 0.3 * DOWN)
        hd = heading("The playground")
        self.narrate("Here is the playground. A generic engine model: shells for the casings, a beam for the shaft, "
                     "about ten thousand elements.")
        self.play(Write(hd), FadeIn(fem))
        e1 = VGroup(text("engine model", 26, GREY_A), number(9976, size=40)).arrange(RIGHT, buff=0.3)
        e1.move_to(3.3 * RIGHT + 2.2 * UP)
        self.play(FadeIn(e1))
        dz = VGroup(text("design zone: pylon + mounts", 26, ACCENT), text("clamped to the wing", 24, GREY_A)).arrange(DOWN, aligned_edge=LEFT)
        dz.move_to(3.3 * RIGHT + 1.2 * UP)
        arr = Arrow(dz.get_left() + 0.1 * LEFT, fem.get_center() + 0.3 * RIGHT + 0.9 * UP, color=ACCENT, buff=0.1)
        self.narrate("Above it, the grey block is everything the aircraft maker controls: the space for the pylon and "
                     "the engine mounts, clamped to the wing.")
        self.play(FadeIn(dz), GrowArrow(arr))
        rows = VGroup()
        for lab, v in (("brick elements", 486400), ("unknowns", 1529847), ("stress points", 3891200)):
            nm = number(0, size=36)
            rows.add(VGroup(text(lab, 26, GREY_A), nm).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, aligned_edge=RIGHT, buff=0.25).move_to(3.3 * RIGHT + 0.6 * DOWN)
        self.narrate("It is cut into four hundred eighty-six thousand brick elements: one and a half million unknowns, "
                     "almost four million points where stress must be checked.")
        self.play(FadeIn(rows))
        self.play(*[ChangeDecimalToValue(r[1], v) for r, v in zip(rows, (486400, 1529847, 3891200))], run_time=3)
        lc = card("load_cases", height=1.5).move_to(3.3 * RIGHT + 2.5 * DOWN)
        self.narrate("Three loads: thrust along the axis, a lateral load, a vertical load.")
        self.play(FadeIn(lc, shift=UP * 0.2))
        self.hush()
        prob = MathTex(r"\min\ \text{volume}\quad\text{s.t.}\quad \sigma_{VM}\le\sigma_{allow},\quad \Delta\mathrm{TSFC}\,\%\le T_0",
                       font_size=40).to_edge(DOWN, buff=0.35)
        bg = BackgroundRectangle(prob, fill_color=config.background_color, fill_opacity=0.95, buff=0.2)
        self.narrate("The question: the lightest structure in this block that never exceeds its allowable stress, and "
                     "keeps delta TSFC below a target.")
        self.play(FadeOut(lc), FadeIn(bg), Write(prob), run_time=2)
        self.clear_all()


# ================================================================== 5. How it's usually done
class S05Usual(Narrated):
    def construct(self):
        hd = heading("How it's usually done")
        boxes = VGroup(*[RoundedRectangle(corner_radius=0.15, width=4.1, height=4.2, color=GREY_D) for _ in range(3)]).arrange(RIGHT, buff=0.3).shift(0.3 * DOWN)
        titles = VGroup(*[text(s, 26, GREY_A).next_to(b, UP, buff=0.12) for s, b in zip(("Sizing", "Compliance topology", "Mount search"), boxes)])
        refs = VGroup(*[text(s, 18, GREY_B).next_to(b, DOWN, buff=0.12) for s, b in zip(("Bettebghor et al. 2013", "Remouchamps et al. 2011", "Xue et al. 2012"), boxes)])
        self.play(Write(hd), Create(boxes), FadeIn(titles))
        # (a) sizing: a fixed pylon outline with panels whose thickness changes
        b0 = boxes[0]
        outline = Polygon(b0.get_center() + np.array([-1.6, 0.9, 0]), b0.get_center() + np.array([1.6, 0.9, 0]),
                          b0.get_center() + np.array([1.2, -0.9, 0]), b0.get_center() + np.array([-1.2, -0.3, 0]), color=GREY_A)
        panels = VGroup(*[Line(b0.get_center() + np.array([x, 0.9, 0]), b0.get_center() + np.array([x, -0.6 - 0.15 * x, 0]),
                               color=ACCENT, stroke_width=4) for x in (-0.8, 0.0, 0.8)])
        self.narrate("The usual approach starts from an architecture someone already drew, and sizes it: thicker here, "
                     "thinner there. Engine and pylon have even been sized together this way.")
        self.play(Create(outline), Create(panels), FadeIn(refs[0]))
        self.play(panels[0].animate.set_stroke(width=12), panels[2].animate.set_stroke(width=2), run_time=1.2)
        self.play(panels[1].animate.set_stroke(width=9), panels[0].animate.set_stroke(width=6), run_time=1.2)
        no = text("can't invent a new load path", 22, BAD).move_to(b0.get_bottom() + 0.5 * UP)
        self.narrate("But sizing can't invent a new load path.")
        self.play(FadeIn(no))
        # (b) compliance topology optimization: replay the SIMP run, small
        d = np.load(DATA / "simp.npz")["hist"]
        it = ValueTracker(0)
        img = always_redraw(lambda: field(d[int(it.get_value())], NELX, NELY, 3.6).move_to(boxes[1].get_center() + 0.3 * UP))
        self.narrate("Topology optimization can: it decides where material exists at all. It has been used on pylons, "
                     "but to make them stiff, not to protect the engine's clearances.")
        self.add(img)
        self.play(it.animate.set_value(len(d) - 1), FadeIn(refs[1]), run_time=3)
        no2 = text("stiff pylon  ≠  engine-friendly", 22, BAD).move_to(boxes[1].get_bottom() + 0.5 * UP)
        self.narrate("And a stiffer pylon is not automatically a better engine neighbour: what matters is how the engine "
                     "deforms, not how much the pylon does.")
        self.play(FadeIn(no2))
        # (c) heuristic search of mount positions on a small region
        b2 = boxes[2]
        region = Rectangle(width=2.6, height=1.6, color=GREY_A).move_to(b2.get_center() + 0.3 * UP)
        rng = np.random.default_rng(4)
        ants = VGroup(*[Dot(region.get_center() + np.array([rng.uniform(-1.2, 1.2), rng.uniform(-0.7, 0.7), 0]), radius=0.06, color=ACCENT) for _ in range(8)])
        self.narrate("Other studies optimized the mount positions with heuristics, on a small region.")
        self.play(Create(region), FadeIn(ants), FadeIn(refs[2]))
        for _ in range(3):
            self.play(*[a.animate.move_to(region.get_center() + np.array([rng.uniform(-1.2, 1.2), rng.uniform(-0.7, 0.7), 0])) for a in ants], run_time=0.6)
        gap = text("The gap: topology optimization, industrial scale, fuel burn and stress in the loop", 28, ACCENT).to_edge(DOWN, buff=0.3)
        self.narrate("The gap: topology optimization, at industrial scale, with fuel consumption and stress inside the loop.")
        self.play(FadeOut(refs), Write(gap), run_time=2)
        self.clear_all()


# ================================================================== 6. SIMP
class S06Simp(Narrated):
    def construct(self):
        hd = heading("Idea 1: let every element decide")
        rng = np.random.default_rng(0)
        rnd = rng.uniform(0, 1, NELX * NELY)
        im = field(rnd, NELX, NELY, 7).shift(0.2 * DOWN)
        l0 = text("0 = void", 26, GREY_A).next_to(im, DOWN).shift(2 * LEFT)
        l1 = text("1 = solid", 26, SOLVED).next_to(im, DOWN).shift(2 * RIGHT)
        self.narrate("Give every element a number between zero and one: void or solid. That's the density.")
        self.play(Write(hd), FadeIn(im), FadeIn(l0), FadeIn(l1))
        grey = field(np.full(NELX * NELY, 0.5), NELX, NELY, 7).move_to(im)
        self.narrate("If grey were allowed for free, the optimizer would happily paint everything grey.")
        self.play(FadeTransform(im, grey), run_time=1.5)
        self.hush()
        self.play(FadeOut(grey), FadeOut(l0), FadeOut(l1))
        p = ValueTracker(1.0)
        ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 0.5], x_length=4.6, y_length=4.0,
                  axis_config={"color": GREY_B, "include_tip": False, "include_numbers": True, "font_size": 22}).shift(3 * LEFT + 0.4 * DOWN)
        xl = text("density", 22, GREY_A).next_to(ax.x_axis, DOWN, buff=0.4)
        yl = text("stiffness", 22, GREY_A).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.4)
        cur = always_redraw(lambda: ax.plot(lambda x: x ** p.get_value(), x_range=[0, 1], color=ACCENT, stroke_width=5))
        dot = always_redraw(lambda: Dot(ax.c2p(0.5, 0.5 ** p.get_value()), color=ACCENT))
        val = always_redraw(lambda: MathTex(f"E(0.5)={0.5 ** p.get_value():.3f}\\,E", font_size=34).move_to(3 * RIGHT + 0.6 * DOWN))
        eq = always_redraw(lambda: MathTex(f"E(x)=x^{{{p.get_value():.1f}}}\\,E", font_size=44).move_to(3 * RIGHT + 0.6 * UP))
        self.narrate("So stiffness is made to grow like the density cubed: half-dense material gives only an eighth of "
                     "the stiffness for half the weight. Grey stops paying, and the design turns black and white.")
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), Create(cur), FadeIn(dot), FadeIn(eq), FadeIn(val))
        self.play(p.animate.set_value(3.0), run_time=3)
        self.hush()
        self.play(*[FadeOut(m) for m in (ax, xl, yl, cur, dot, eq, val)])
        d = np.load(DATA / "simp.npz")
        hist, comp = d["hist"], d["comp"]
        N = len(hist) - 1
        W = 6.6
        frame = Rectangle(width=W, height=W / 2, color=GREY_B).shift(2.4 * LEFT + 0.5 * DOWN)
        it = ValueTracker(0)
        img = always_redraw(lambda: field(hist[int(it.get_value())], NELX, NELY, W).move_to(frame))
        load = Arrow(frame.get_right() + 1.0 * UP, frame.get_right(), color=BAD, buff=0)
        cnt = always_redraw(lambda: text(f"iteration {int(it.get_value()):2d}    compliance {comp[int(it.get_value())]:.1f}", 24)
                            .next_to(frame, UP).align_to(frame, LEFT))
        ax2 = Axes(x_range=[0, N, 20], y_range=[0, 300, 100], x_length=3.8, y_length=3,
                   axis_config={"color": GREY_B, "include_tip": False, "include_numbers": True, "font_size": 18}).shift(4.3 * RIGHT + 0.5 * DOWN)
        gr = always_redraw(lambda: ax2.plot_line_graph(np.arange(int(it.get_value()) + 1), np.minimum(comp[:int(it.get_value()) + 1], 300),
                                                       add_vertex_dots=False, line_color=ACCENT, stroke_width=3))
        self.narrate("Here is a small cantilever, clamped on the left, pushed down on the right. Watch the load path appear.")
        self.add(img)
        self.play(Create(frame), FadeIn(clamp_marks(frame)), GrowArrow(load), Create(ax2), FadeIn(cnt))
        self.add(gr)
        self.play(it.animate.set_value(N), run_time=9, rate_func=lambda s: s ** 1.6)
        self.wait(1)
        self.clear_all()


# ================================================================== 7. Traps and filter
class S07Filter(Narrated):
    def construct(self):
        hd = heading("Two traps, and the filter")
        a = np.load(DATA / "simp_nofilter_60.npz")["hist"][-1]
        b = np.load(DATA / "simp_nofilter_120.npz")["hist"][-1]
        fa = np.load(DATA / "simp.npz")["hist"][-1]
        fb = np.load(DATA / "simp_filter_120.npz")["hist"][-1]
        ia = field(a, 60, 30, 5.6).move_to(3.3 * LEFT + 0.6 * UP)
        ib = field(b, 120, 60, 5.6).move_to(3.3 * RIGHT + 0.6 * UP)
        la = text("60 × 30, no filter", 24, GREY_A).next_to(ia, DOWN)
        lb = text("120 × 60, no filter", 24, GREY_A).next_to(ib, DOWN)
        self.narrate("Left alone, this goes wrong in two ways.")
        self.play(Write(hd), FadeIn(ia), FadeIn(la))
        zoom = Rectangle(width=1.4, height=1.2, color=BAD, stroke_width=4).move_to(ia.get_center() + np.array([1.55, 0.0, 0]))
        cb = text("checkerboards", 26, BAD).next_to(la, DOWN)
        self.narrate("It invents checkerboards: alternating black and white cells that the finite elements wrongly see as stiff.")
        self.play(Create(zoom), FadeIn(cb))
        md = text("a finer mesh gives a different design", 26, BAD).next_to(lb, DOWN)
        self.narrate("And refine the mesh, and you get a different, finer design: no answer at all, just more detail.")
        self.play(FadeIn(ib), FadeIn(lb))
        self.play(FadeIn(md))
        self.hush()
        self.play(*[FadeOut(m) for m in (ia, ib, la, lb, zoom, cb, md)])
        grid = VGroup(*[Square(0.4, stroke_width=1, stroke_color=GREY_D) for _ in range(14 * 7)]).arrange_in_grid(7, 14, buff=0).shift(0.4 * UP)
        rng = np.random.default_rng(3)
        for sq in grid:
            sq.set_fill(SOLVED, opacity=float(rng.uniform() > 0.5))
        disk = Circle(0.9, color=ACCENT, stroke_width=4).move_to(grid[3 * 14 + 3])
        fe = MathTex(r"x^{phys}_e=\frac{\sum_j w_{ej}\,x_j}{\sum_j w_{ej}},\qquad w_{ej}=\max(0,\,r-\|X_e-X_j\|)", font_size=36).to_edge(DOWN, buff=0.6)
        self.narrate("The cure is a filter: each element's physical density is a weighted average of its neighbours "
                     "within a fixed radius.")
        self.play(FadeIn(grid), Create(disk), Write(fe))
        self.play(disk.animate.move_to(grid[3 * 14 + 10]), run_time=2)
        self.hush()
        self.play(FadeOut(grid), FadeOut(disk), FadeOut(fe))
        ja = field(fa, 60, 30, 5.6).move_to(3.3 * LEFT + 0.6 * UP)
        jb = field(fb, 120, 60, 5.6).move_to(3.3 * RIGHT + 0.6 * UP)
        ka = text("60 × 30, filtered", 24, GOOD).next_to(ja, DOWN)
        kb = text("120 × 60, filtered", 24, GOOD).next_to(jb, DOWN)
        self.narrate("Checkerboards vanish, and the design stops depending on the mesh.")
        self.play(FadeIn(ja), FadeIn(ka))
        self.play(FadeIn(jb), FadeIn(kb))
        mg = text("half a million irregular elements: the filter matrix is built with a multigrid strategy", 24, ACCENT).to_edge(DOWN, buff=0.5)
        self.narrate("On a mesh with half a million irregular elements, just finding everyone's neighbours is expensive; "
                     "the thesis builds that filter matrix with a multigrid strategy.")
        self.play(FadeIn(mg))
        self.clear_all()


# ================================================================== 8. Superelements (toy)
class S08Super(Narrated):
    def construct(self):
        hd = heading("Fitting the engine in: superelements")
        eng = card("engine_labels", height=3.0).move_to(3.4 * RIGHT + 1.3 * UP)
        src = text("from the engine maker: Nastran / Abaqus", 24, GREY_A).next_to(eng, DOWN)
        self.narrate("The engine model comes from the engine maker, in Nastran or Abaqus. We don't want to re-implement "
                     "it, and we can't afford to re-solve it at every iteration.")
        self.play(Write(hd), FadeIn(eng), FadeIn(src))

        def spring(a, b, color=SOLVED):
            pts = [a]
            for k in range(1, 12):
                pts.append(a + (b - a) * k / 12 + (0.18 if k % 2 else -0.18) * UP)
            pts.append(b)
            return VMobject(color=color, stroke_width=4).set_points_as_corners(pts)

        y = 1.2 * DOWN
        A, M, B = 6 * LEFT + y, 3.6 * LEFT + y, 1.2 * LEFT + y
        s1, s2 = spring(A, M), spring(M, B)
        nodes = VGroup(Dot(A, color=ACCENT, radius=0.12), Dot(M, color=GREY_A, radius=0.12), Dot(B, color=ACCENT, radius=0.12))
        k1 = MathTex("k_1=2", font_size=32).next_to(s1, UP)
        k2 = MathTex("k_2=3", font_size=32).next_to(s2, UP)
        self.narrate("Take two springs in a row. If nobody ever pushes on the middle node, we can solve for it once and "
                     "for all.")
        self.play(Create(s1), Create(s2), FadeIn(nodes), FadeIn(k1), FadeIn(k2))
        K = np.array([[2.0, -2, 0], [-2, 5, -3], [0, -3, 3]])
        b, i = [0, 2], [1]
        Kse = K[np.ix_(b, b)] - K[np.ix_(b, i)] @ np.linalg.inv(K[np.ix_(i, i)]) @ K[np.ix_(i, b)]
        km = MathTex(r"K=\begin{bmatrix}2&-2&0\\-2&5&-3\\0&-3&3\end{bmatrix}", font_size=34).move_to(3.6 * LEFT + 1.2 * UP)
        self.play(Write(km))
        frac = lambda v: f"{v * 5:.0f}/5" if abs(v * 5 - round(v * 5)) < 1e-9 else f"{v:.2f}"
        kse = MathTex(r"K_{SE}=K_{bb}-K_{bi}K_{ii}^{-1}K_{ib}=\begin{bmatrix}" + frac(Kse[0, 0]) + "&" + frac(Kse[0, 1]) + r"\\" +
                      frac(Kse[1, 0]) + "&" + frac(Kse[1, 1]) + r"\end{bmatrix}", font_size=34).move_to(2.5 * LEFT + 2.9 * DOWN)
        one = spring(A, B, color=GOOD)
        k12 = MathTex(r"k=\tfrac{6}{5}", font_size=34, color=GOOD).next_to(one, UP)
        self.narrate("What remains is a single spring between the ends, with exactly the same behaviour.")
        self.play(Write(kse), run_time=2)
        self.play(ReplacementTransform(VGroup(s1, s2), one), FadeOut(nodes[1]), FadeOut(k1), ReplacementTransform(k2, k12))
        ex = text("exact, not an approximation", 26, GOOD).next_to(kse, UP, buff=0.25).align_to(kse, LEFT)
        self.narrate("That's a superelement: K b b minus K b i, K i i inverse, K i b. Exact, not an approximation.")
        self.play(FadeIn(ex), Indicate(kse))
        rng = np.random.default_rng(2)
        ctr = eng.get_center()
        inner = VGroup(*[Dot(ctr + np.array([rng.uniform(-2.2, 2.2), rng.uniform(-1.2, 1.2), 0]), radius=0.05, color=GREY_B) for _ in range(60)])
        iface = VGroup(*[Dot(ctr + np.array([x, 1.35, 0]), radius=0.07, color=ACCENT) for x in np.linspace(-1.6, 1.6, 9)])
        self.narrate("The thesis does this for the whole engine: only the nodes that touch the pylon remain, and the tip "
                     "clearances can still be recovered from them.")
        self.play(FadeIn(inner), FadeIn(iface))
        self.play(FadeOut(inner, scale=0.3), Indicate(iface, color=ACCENT), run_time=2)
        self.clear_all()


# ================================================================== 9. Mesh tying
class S09Tying(Narrated):
    def construct(self):
        hd = heading("Gluing meshes that don't match")
        x0 = -4.4
        left = VGroup(*[Square(0.6).set_stroke(SOLVED, 2).move_to([x0 - 0.3 - 0.6 * i, 1.5 - 0.3 - 0.6 * j, 0]) for i in range(4) for j in range(6)])
        right = VGroup(*[Rectangle(width=0.9, height=0.9).set_stroke(ACCENT, 2).move_to([x0 + 0.45 + 0.9 * i, 1.5 - 0.45 - 0.9 * j, 0]) for i in range(4) for j in range(4)])
        yl = [1.5 - 0.6 * j for j in range(7)]
        yr = [1.5 - 0.9 * j for j in range(5)]
        dl = VGroup(*[Dot([x0, y, 0], radius=0.07, color=SOLVED) for y in yl])
        dr = VGroup(*[Dot([x0, y, 0], radius=0.07, color=ACCENT) for y in yr])
        self.narrate("The engine's mesh and the design block's mesh were made separately. At their interface, nodes "
                     "don't face each other.")
        self.play(Write(hd), Create(left), Create(right))
        self.play(FadeIn(dl), FadeIn(dr), right.animate.shift(0.0 * RIGHT))
        tear = VGroup(*[Line([x0, y, 0], [x0 + 0.25, y, 0], color=BAD, stroke_width=6) for y in yr[1:-1]])
        mom = VGroup(Arc(radius=0.6, start_angle=-PI / 3, angle=2 * PI / 3, color=BAD).add_tip().move_to([x0 + 4.0, -0.3, 0]),
                     text("moment not transmitted", 24, BAD).move_to([x0 + 4.0, -2.3, 0]))
        self.narrate("Glue them carelessly and forces leak: the interface no longer transmits the right moment.")
        self.play(right.animate.shift(0.25 * RIGHT), dr.animate.shift(0.25 * RIGHT), Create(tear))
        self.play(FadeIn(mom))
        self.hush()
        self.play(right.animate.shift(0.25 * LEFT), dr.animate.shift(0.25 * LEFT), FadeOut(tear), FadeOut(mom))
        meth = VGroup(text("Mortar", 30), text("Internodes", 30), text("Radial basis functions (RL-RBF)", 30),
                      text("New: weighted average continuity approach", 30, ACCENT),
                      text("+ a correction restoring the balance of moments", 28, GOOD)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        meth.move_to(2.9 * RIGHT + 0.3 * DOWN)
        ok = text("tied: forces and moments balanced", 24, GOOD).move_to([x0, -2.4, 0])
        self.narrate("The thesis implements and benchmarks four ways of tying them: Mortar, Internodes, radial basis "
                     "functions, and a new one, the weighted average continuity approach, together with a correction "
                     "that restores the balance of moments exactly.")
        self.play(LaggedStart(*[FadeIn(m, shift=RIGHT * 0.2) for m in meth[:3]], lag_ratio=0.5), run_time=3)
        self.play(FadeIn(meth[3], shift=RIGHT * 0.2))
        self.play(FadeIn(meth[4], shift=RIGHT * 0.2), FadeIn(ok))
        self.clear_all()


# ================================================================== 10/11. Singular optima (toy)
L1, L2, S1LIM, S2LIM = 1.0, 2.0, 1.0, 4.0


def stresses(x1, x2):
    """Two bars hanging one rigid plate (P = 1, E = 1): same stretch, so stress = E u / L."""
    u = 1.0 / (x1 / L1 + x2 / L2)
    return u / L1, u / L2


def relaxed_ks(x1, x2, P=4.0):
    s1, s2 = stresses(x1, x2)
    g = np.array([x1 * (s1 / S1LIM - 1), x2 * (s2 / S2LIM - 1)])
    m = g.max(0)
    return m + np.log(np.mean(np.exp(P * (g - m)), 0)) / P


def run_slsqp(x0, relaxed):
    from scipy.optimize import minimize
    path = [np.array(x0, float)]
    if relaxed:
        cons = [{"type": "ineq", "fun": lambda x: -relaxed_ks(x[0], x[1])}]
    else:
        cons = [{"type": "ineq", "fun": lambda x: [1 - stresses(*x)[0] / S1LIM, 1 - stresses(*x)[1] / S2LIM]}]
    minimize(lambda x: x[0] + 2 * x[1], x0, method="SLSQP", bounds=[(1e-3, 2), (1e-3, 3)], constraints=cons,
             callback=lambda xk: path.append(xk.copy()), options={"maxiter": 200})
    return np.array(path)


def design_plane():
    ax = Axes(x_range=[0, 1.6, 0.5], y_range=[0, 2.6, 0.5], x_length=5.2, y_length=5.4,
              axis_config={"color": GREY_B, "include_tip": False, "include_numbers": True, "font_size": 20}).shift(3.0 * RIGHT + 0.4 * DOWN)
    xl = MathTex("x_1", font_size=30).next_to(ax.x_axis, RIGHT, buff=0.1)
    yl = MathTex("x_2", font_size=30).next_to(ax.y_axis, UP, buff=0.1)
    return ax, VGroup(xl, yl)


def region_image(ax, mask, color, alpha=0.45):
    h, w = mask.shape
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., :3] = np.array(color)
    rgba[..., 3] = (mask * 255 * alpha).astype(np.uint8)
    img = ImageMobject(rgba)
    img.stretch_to_fit_width(ax.c2p(1.6, 0)[0] - ax.c2p(0, 0)[0])
    img.stretch_to_fit_height(ax.c2p(0, 2.6)[1] - ax.c2p(0, 0)[1])
    img.move_to((ax.c2p(0, 0) + ax.c2p(1.6, 2.6)) / 2)
    return img


def grid_masks(res=400):
    xs = np.linspace(1e-4, 1.6, res)
    ys = np.linspace(1e-4, 2.6, res)[::-1]
    X1, X2 = np.meshgrid(xs, ys)
    s1, s2 = stresses(X1, X2)
    orig = (s1 <= S1LIM) & (s2 <= S2LIM)
    rel = relaxed_ks(X1, X2) <= 0
    return orig, rel


def two_bars():
    ceil1 = Line(6.4 * LEFT + 1.6 * UP, 4.6 * LEFT + 1.6 * UP, color=GREY_B, stroke_width=6)
    ceil2 = Line(3.6 * LEFT + 2.6 * UP, 1.8 * LEFT + 2.6 * UP, color=GREY_B, stroke_width=6)
    plate = Rectangle(width=4.8, height=0.25, fill_color=GREY_C, fill_opacity=1, stroke_width=0).move_to(3.6 * LEFT + 0.6 * DOWN)
    b1 = Line(5.5 * LEFT + 1.6 * UP, 5.5 * LEFT + 0.48 * DOWN, color=BAD, stroke_width=10)
    b2 = Line(2.7 * LEFT + 2.6 * UP, 2.7 * LEFT + 0.48 * DOWN, color=SOLVED, stroke_width=10)
    l1 = text("short, weak", 22, BAD).next_to(b1, LEFT, buff=0.15)
    l2 = text("long, strong", 22, SOLVED).next_to(b2, RIGHT, buff=0.15)
    load = Arrow(plate.get_bottom(), plate.get_bottom() + 1.1 * DOWN, color=WHITE, buff=0)
    return VGroup(ceil1, ceil2, plate, b1, b2, l1, l2, load)


class S10Singular(Narrated):
    def construct(self):
        hd = heading("Stress, and the optimum you can't reach")
        bars = two_bars()
        self.narrate("Now stress. Two bars share a load. They stretch by the same amount, so the short bar is always the "
                     "more stressed one, whatever its thickness.")
        self.play(Write(hd), Create(bars), run_time=2)
        s = MathTex(r"\sigma_1=\frac{E\,u}{L_1}\ \text{does not depend on } x_1", font_size=32).move_to(3.6 * LEFT + 2.9 * DOWN)
        self.play(Write(s))
        self.narrate("Make its material weak, and it can never be safe, unless it isn't there at all.")
        self.play(Indicate(bars[3], color=BAD), bars[5].animate.set_color(BAD))
        ax, labs = design_plane()
        orig, _ = grid_masks()
        reg = region_image(ax, orig, (88, 196, 221))
        spike = Line(ax.c2p(0, 0.25), ax.c2p(0, 2.6), color=SOLVED, stroke_width=8)
        self.narrate("Look at the safe designs: a big region, and this spike along the axis, where the short bar has vanished.")
        self.play(Create(ax), FadeIn(labs))
        self.play(FadeIn(reg), Create(spike))
        heavy = Dot(ax.c2p(1, 0), color=BAD, radius=0.1)
        light = Dot(ax.c2p(0, 0.25), color=GOOD, radius=0.1)
        lh = text("volume 1", 22, BAD).next_to(heavy, UP, buff=0.15)
        lg = text("volume 0.5", 22, GOOD).next_to(light, RIGHT, buff=0.2)
        cont = VGroup(*[DashedLine(ax.c2p(0, v / 2), ax.c2p(v, 0), color=GREY_C, stroke_width=2) for v in (0.5, 1.0)])  # volume x1 + 2 x2 = v
        self.narrate("The lightest design is at the tip of the spike: half the volume.")
        self.play(Create(cont), FadeIn(heavy), FadeIn(lh), FadeIn(light), FadeIn(lg))
        path = run_slsqp([0.2, 2.0], relaxed=False)
        trail = VMobject(color=ACCENT, stroke_width=4).set_points_as_corners([ax.c2p(*p) for p in path])
        walker = Dot(ax.c2p(*path[0]), color=ACCENT, radius=0.09)
        self.narrate("But the spike has no thickness. Any trace of the short bar, however thin, is unsafe, and an "
                     "optimizer that keeps every density slightly above zero never gets onto it.")
        self.play(FadeIn(walker))
        self.play(Create(trail), MoveAlongPath(walker, trail.copy()), run_time=3)
        self.play(Flash(heavy, color=BAD))
        name = text("a singular optimum", 30, ACCENT).to_edge(DOWN, buff=0.3)
        self.narrate("Optima like this are called singular, and topology optimization is full of them.")
        self.play(FadeIn(name))
        self.clear_all()


class S11Relax(Narrated):
    def construct(self):
        hd = heading("Relax and aggregate")
        ax, labs = design_plane()
        orig, rel = grid_masks()
        reg = region_image(ax, orig, (88, 196, 221))
        spike = Line(ax.c2p(0, 0.25), ax.c2p(0, 2.6), color=SOLVED, stroke_width=8)
        self.add(hd, ax, labs, reg, spike)
        f1 = MathTex(r"\bar g_i = x_i\left(\frac{\sigma_i}{\sigma_{i,lim}}-1\right)", font_size=40).move_to(3.6 * LEFT + 1.8 * UP)
        self.narrate("The fix comes in two moves. First, multiply each stress violation by the density of its element. "
                     "A vanishing bar now has a vanishing violation: the danger fades smoothly as the bar disappears.")
        self.play(Write(f1), run_time=2)
        rng = np.random.default_rng(5)
        cloud = VGroup(*[Dot([rng.uniform(-6.4, -1), rng.uniform(-1.6, 0.4), 0], radius=0.025,
                             color=interpolate_color(ManimColor(SOLVED), ManimColor(BAD), rng.uniform())) for _ in range(400)])
        f2 = MathTex(r"G_{KS}=\frac{1}{P}\ln\Big(\frac{1}{N}\sum_i e^{P\bar g_i}\Big)\ \le\ \max_i \bar g_i", font_size=36).move_to(3.6 * LEFT + 2.6 * DOWN)
        self.narrate("Second, there are almost four million stress points in the pylon. Instead of four million "
                     "constraints, take a smooth estimate of the largest one, the KS function, built to sit slightly "
                     "below the true maximum.")
        self.play(LaggedStart(*[FadeIn(d) for d in cloud], lag_ratio=0.003), run_time=1.5)
        one = Dot(3.6 * LEFT + 0.6 * DOWN, color=ACCENT, radius=0.16)
        self.play(*[d.animate.move_to(one) for d in cloud], run_time=1.5)
        self.play(FadeOut(cloud), FadeIn(one), Write(f2))
        reg2 = region_image(ax, rel, (95, 211, 141), alpha=0.5)
        p1 = run_slsqp([0.2, 2.0], relaxed=False)
        p2 = run_slsqp([0.2, 2.0], relaxed=True)
        t1 = VMobject(color=BAD, stroke_width=3).set_points_as_corners([ax.c2p(*p) for p in p1])
        t2 = VMobject(color=GOOD, stroke_width=4).set_points_as_corners([ax.c2p(*p) for p in p2])
        w2 = Dot(ax.c2p(*p2[0]), color=GOOD, radius=0.09)
        res = text(f"same start: volume {p1[-1][0] + 2 * p1[-1][1]:.2f}  vs  {p2[-1][0] + 2 * p2[-1][1]:.2f}", 24, GOOD).next_to(ax, DOWN, buff=0.35)
        self.narrate("That small slack gives the spike a width: a corridor the optimizer can walk down, to the lighter design.")
        self.play(FadeIn(reg2), run_time=1.5)
        self.play(Create(t1), run_time=1)
        self.play(Create(t2), MoveAlongPath(w2, t2.copy()), run_time=3)
        self.play(FadeIn(res))
        p3 = run_slsqp([0.5, 1.5], relaxed=True)
        t3 = VMobject(color=ACCENT, stroke_width=3).set_points_as_corners([ax.c2p(*p) for p in p3])
        caveat = text(f"another start: volume {p3[-1][0] + 2 * p3[-1][1]:.2f}. Reachable, not guaranteed.", 22, ACCENT).next_to(res, DOWN, buff=0.15)
        self.narrate("It is a local method, though: started elsewhere, it can still settle for the heavy design. The "
                     "light optimum becomes reachable, not guaranteed.")
        self.play(Create(t3), FadeIn(caveat), run_time=2)
        uar = text("unified aggregation and relaxation", 30, ACCENT).move_to(3.6 * LEFT + 0.5 * UP)
        self.narrate("One constraint instead of four million, and singular optima become reachable. The thesis calls "
                     "this unified aggregation and relaxation.")
        self.play(FadeOut(one), Write(uar))
        self.clear_all()


# ================================================================== 12. Adjoint
class S12Adjoint(Narrated):
    def construct(self):
        hd = heading("Gradients for the price of one solve")
        nv = VGroup(text("design variables", 28, GREY_A), number(243200, size=48, color=ACCENT)).arrange(RIGHT, buff=0.4).shift(2.0 * UP)
        self.narrate("The optimizer needs to know which way to move every one of the two hundred forty-three thousand "
                     "density variables.")
        self.play(Write(hd), FadeIn(nv))
        fd_n = number(0, size=44, color=BAD)
        fd = VGroup(text("nudge one by one: extra solves per iteration", 26), fd_n).arrange(RIGHT, buff=0.4).shift(0.5 * UP)
        self.narrate("Nudging them one by one would cost one finite-element solve each, per iteration.")
        self.play(FadeIn(fd))
        self.play(ChangeDecimalToValue(fd_n, 243200), run_time=3)
        ad = VGroup(text("adjoint: extra solves per iteration", 26), MathTex(r"1\ \text{per response}", font_size=44, color=GOOD)).arrange(RIGHT, buff=0.4).shift(0.7 * DOWN)
        eq = MathTex(r"K\lambda=\frac{\partial O}{\partial U},\qquad \frac{dO}{dx_e}=\frac{\partial O}{\partial x_e}-\lambda^T\frac{\partial K}{\partial x_e}U",
                     font_size=38).shift(2.2 * DOWN)
        self.narrate("The adjoint method gets all of them from one extra solve per response: one for the volume, which "
                     "is free, one for the stress constraint, one for delta TSFC.")
        self.play(FadeIn(ad))
        self.play(Write(eq), run_time=2)
        note = text("derived in the thesis for the stress and fuel-consumption responses", 24, ACCENT).to_edge(DOWN, buff=0.4)
        self.narrate("The thesis derives these adjoints for the fuel-consumption and stress responses.")
        self.play(FadeIn(note))
        self.clear_all()


# ================================================================== 13. GGP
class S13Ggp(Narrated):
    def construct(self):
        hd = heading("Idea 2: build with parts")
        a = np.load(DATA / "simp.npz")["hist"][-1]
        organic = field(a, NELX, NELY, 5.0).move_to(3.4 * LEFT + 0.8 * UP)
        la = text("densities: free, but organic", 24, GREY_A).next_to(organic, DOWN)
        self.narrate("Density designs are free, but organic: someone still has to turn them into parts.")
        self.play(Write(hd), FadeIn(organic), FadeIn(la))
        bar = RoundedRectangle(corner_radius=0.3, width=3.6, height=0.6, color=ACCENT, fill_opacity=0.4).rotate(0.35).move_to(3.4 * RIGHT + 0.8 * UP)
        pars = MathTex(r"(x_c,\ y_c,\ L,\ h,\ \theta)", font_size=36).next_to(bar, DOWN, buff=0.6)
        self.narrate("The other family starts from parts: bars, plates, boxes, each described by a few numbers, its "
                     "position, length, thickness and angle. They move and grow; the mesh stays fixed.")
        self.play(FadeIn(bar), Write(pars))
        self.play(bar.animate.shift(0.4 * UP).rotate(-0.6), run_time=1.2)
        self.play(bar.animate.stretch(0.7, 0), run_time=1)
        self.hush()
        self.play(*[FadeOut(m) for m in (organic, la, bar, pars)])
        n, cs = 14, 0.34
        org = np.array([-6.4, -2.6, 0])
        cells = VGroup(*[Square(cs, stroke_width=1, stroke_color=GREY_D).move_to(org + np.array([(i + 0.5) * cs, (j + 0.5) * cs, 0]))
                         for i in range(n) for j in range(n)])
        th = ValueTracker(0.45)
        cx = ValueTracker(2.4)

        def centre():
            return org + np.array([cx.get_value(), 2.38, 0])

        def fill():
            c, t = centre(), th.get_value()
            g = VGroup()
            for sq in cells:
                d = sq.get_center() - c
                s, q = d[0] * np.cos(t) + d[1] * np.sin(t), -d[0] * np.sin(t) + d[1] * np.cos(t)
                w = 0.5 * (1 + np.tanh((1.6 - abs(s)) / 0.12)) * 0.5 * (1 + np.tanh((0.35 - abs(q)) / 0.12))
                g.add(Square(cs, stroke_width=0, fill_color=SOLVED, fill_opacity=w).move_to(sq))
            return g

        fills = always_redraw(fill)
        outline = always_redraw(lambda: RoundedRectangle(corner_radius=0.35, width=3.2 + 0.7, height=0.7, color=ACCENT, stroke_width=3)
                                .rotate(th.get_value()).move_to(centre()))
        win = Square(cs, color=WHITE, stroke_width=3).move_to(cells[7 * n + 7])
        gps = VGroup(*[Dot(win.get_center() + np.array([a * cs / 4, b * cs / 4, 0]), radius=0.025, color=WHITE) for a in (-1, 1) for b in (-1, 1)])
        f = MathTex(r"\delta^{el}=\frac{\int_{D}W(X)\,d\Omega}{\int_{D}d\Omega}", font_size=40).move_to(2.8 * RIGHT + 1.4 * UP)
        self.narrate("To analyse them on that fixed mesh, each element asks: what fraction of a little window around me "
                     "does this bar cover? That fraction becomes its density.")
        self.play(Create(cells), run_time=1)
        self.add(fills, outline)
        self.play(Create(win), FadeIn(gps), Write(f))
        self.play(th.animate.set_value(-0.5), cx.animate.set_value(2.0), run_time=2.5)
        meth = VGroup(text("Moving Morphable Components", 28), text("Geometry Projection", 28), text("Moving Node Approach", 28)).arrange(DOWN, aligned_edge=LEFT).move_to(2.2 * RIGHT + 1.2 * DOWN)
        br = Brace(meth, RIGHT, color=ACCENT)
        gg = text("special cases of\nGGP", 28, ACCENT).next_to(br, RIGHT)
        self.narrate("Three known methods, moving morphable components, geometry projection and the moving node "
                     "approach, look different. The thesis shows they are the same procedure with different choices: "
                     "the generalized geometry projection.")
        self.play(LaggedStart(*[FadeIn(m, shift=LEFT * 0.2) for m in meth], lag_ratio=0.4), run_time=2)
        self.play(GrowFromCenter(br), FadeIn(gg))
        self.clear_all()


# ================================================================== 14. Accuracy of the projection (toy)
class S14Beam(Narrated):
    def construct(self):
        hd = heading("Is the projection accurate?")
        d = np.load(DATA / "bar_hc.npz")
        h, c1, c4, eu = d["h"], d["c1"], d["c4"], d["euler"]
        frame = Rectangle(width=5.0, height=2.5, color=GREY_B).move_to(4.0 * LEFT + 0.9 * UP)
        hv = ValueTracker(h[0])
        barm = always_redraw(lambda: Rectangle(width=5.0, height=hv.get_value() * 0.05, fill_color=SOLVED, fill_opacity=0.9,
                                               stroke_width=0).move_to(frame))
        load = Arrow(frame.get_right() + 0.8 * UP, frame.get_right(), color=BAD, buff=0)
        lab = always_redraw(lambda: MathTex(f"h={hv.get_value():.1f}", font_size=34).next_to(frame, DOWN))
        self.narrate("Before trusting this, check it where we know the answer: one bar, a cantilever, classical beam theory.")
        self.play(Write(hd), Create(frame), FadeIn(clamp_marks(frame)), GrowArrow(load))
        self.add(barm, lab)
        ax = Axes(x_range=[1, 10, 1], y_range=[3, 7, 1], x_length=6.2, y_length=4.6,
                  axis_config={"color": GREY_B, "include_tip": False}, x_axis_config={"include_numbers": True, "font_size": 22}).move_to(3.4 * RIGHT + 0.5 * DOWN)
        ticks = VGroup(*[MathTex(f"10^{k}", font_size=26).next_to(ax.c2p(1, k), LEFT) for k in range(3, 8)])
        yl = text("compliance", 22, GREY_A).next_to(ax, UP, buff=0.1)
        xl = MathTex("h", font_size=30).next_to(ax.x_axis, RIGHT)
        theory = ax.plot_line_graph(h, np.log10(eu), add_vertex_dots=False, line_color=GOOD, stroke_width=4)
        lt = text("Euler beam theory", 22, GOOD).move_to(ax.c2p(7.5, 6.4))
        self.play(Create(ax), FadeIn(ticks), FadeIn(yl), FadeIn(xl))
        self.play(Create(theory), FadeIn(lt), run_time=1.5)
        it = ValueTracker(0)

        def partial(vals, col, w):
            k = max(1, int(it.get_value()))
            return ax.plot_line_graph(h[:k + 1], np.log10(vals[:k + 1]), add_vertex_dots=False, line_color=col, stroke_width=w)

        g1 = always_redraw(lambda: partial(c1, ACCENT, 4))
        g4 = always_redraw(lambda: partial(c4, SOLVED, 4))
        l1 = text("1 point per window", 22, ACCENT).move_to(ax.c2p(7.5, 5.95))
        l4 = text("4 points per window", 22, SOLVED).move_to(ax.c2p(7.5, 5.5))
        self.narrate("For thick bars, the projected model follows the theory, a little on the soft side. For thin bars, "
                     "it's too stiff, and with a single point per window the curve gets wavy, as the bar's edge crosses "
                     "the element rows.")
        self.add(g1)
        self.play(FadeIn(l1), it.animate.set_value(len(h) - 1), hv.animate.set_value(h[-1]), run_time=6, rate_func=linear)
        self.play(Indicate(VGroup(*[Dot(ax.c2p(x, np.log10(y)), radius=0.04) for x, y in zip(h[2:8], c1[2:8])]), color=ACCENT))
        it.set_value(0)
        hv.set_value(h[0])
        self.narrate("More sample points per window smooth it out. That's the kind of knob the thesis maps, for each of "
                     "the three methods.")
        self.add(g4)
        self.play(FadeIn(l4), it.animate.set_value(len(h) - 1), hv.animate.set_value(h[-1]), run_time=5, rate_func=linear)
        src = text("recomputed with the GGP-Python projection (AMMC), thesis Fig. 3.22 settings", 20, GREY_B).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(src))
        self.clear_all()


# ================================================================== 15. Evidence, 2D
class S15Cantilever(Narrated):
    def construct(self):
        d = np.load(DATA / "ggp_repo_GP.npz")
        dens, comps, comp, vol = d["dens"], d["comps"], d["comp"], d["vol"]
        N = len(dens) - 1
        W = 6.4
        cs = W / NELX
        frame = Rectangle(width=W, height=W / 2, color=GREY_B).shift(2.6 * LEFT + 0.3 * DOWN)
        org = frame.get_corner(DL)
        it = ValueTracker(0)
        img = always_redraw(lambda: field(dens[int(it.get_value())].T.flatten(), NELX, NELY, W).move_to(frame))

        def bars():
            g = VGroup()
            for x0, y0, L, hh, t, m in comps[int(it.get_value())]:
                w = float(m) ** 3
                if w < 0.02:
                    continue
                hh = max(hh, 0.05)
                g.add(RoundedRectangle(corner_radius=hh * cs / 2 * 0.999, width=(L + hh) * cs, height=hh * cs, stroke_color=ACCENT,
                                       stroke_width=2, stroke_opacity=w, fill_opacity=0).rotate(t).move_to(org + np.array([x0 * cs, y0 * cs, 0])))
            return g

        bs = always_redraw(bars)
        big = 20
        masks = VGroup(*[Rectangle(width=big, height=big).next_to(frame, dr, buff=0) for dr in (LEFT, RIGHT, UP, DOWN)]).set_style(
            fill_color=config.background_color, fill_opacity=1, stroke_width=0)
        hd = heading("The evidence: a real run")
        load = Arrow(frame.get_right() + 1.0 * UP, frame.get_right(), color=BAD, buff=0)
        cnt = always_redraw(lambda: text(f"iteration {int(it.get_value()):3d}   compliance {comp[int(it.get_value())]:.4g}", 24)
                            .next_to(frame, UP).align_to(frame, LEFT))
        ax = Axes(x_range=[0, N, 100], y_range=[0, 400, 100], x_length=3.8, y_length=3,
                  axis_config={"color": GREY_B, "include_tip": False, "include_numbers": True, "font_size": 18}).shift(4.4 * RIGHT + 0.3 * DOWN)
        gr = always_redraw(lambda: ax.plot_line_graph(np.arange(int(it.get_value()) + 1), np.minimum(comp[:int(it.get_value()) + 1], 400),
                                                      add_vertex_dots=False, line_color=ACCENT, stroke_width=3))
        self.add(img, bs, masks)
        self.narrate("Here's the short cantilever, with eighteen bars, run with the GGP framework and the thesis "
                     "settings: the bars slide, turn and fade into a truss.")
        self.play(Write(hd), Create(frame), FadeIn(clamp_marks(frame)), GrowArrow(load), Create(ax), FadeIn(cnt))
        self.add(gr)
        self.play(it.animate.set_value(N), run_time=12, rate_func=lambda s: s ** 1.2)
        res = text(f"compliance {comp[-1]:.2f}    thesis: 74.94", 28, GOOD).to_edge(DOWN, buff=1.0)
        self.narrate("Compliance seventy-four point two; the thesis reports seventy-four point nine.")
        self.play(FadeIn(res))
        self.clear_all()
        hd2 = heading("Same benchmark, three methods (thesis, 4 points per window)")
        vals = (("Moving Morphable Components", 84.50, 153), ("Geometry Projection", 74.94, 122), ("Moving Node Approach", 84.16, 150))
        bx = Axes(x_range=[0, 3, 1], y_range=[0, 100, 20], x_length=7, y_length=4.2,
                  axis_config={"color": GREY_B, "include_tip": False}, y_axis_config={"include_numbers": True, "font_size": 20}).shift(0.4 * DOWN)
        cols = VGroup(*[Rectangle(width=1.4, height=bx.c2p(0, v)[1] - bx.c2p(0, 0)[1], fill_color=GOOD if v < 80 else SOLVED,
                                  fill_opacity=0.85, stroke_width=0).move_to(bx.c2p(k + 0.5, v / 2)) for k, (_, v, _) in enumerate(vals)])
        nums = VGroup(*[text(f"{v:.2f}", 24).next_to(c, UP) for c, (_, v, _) in zip(cols, vals)])
        names = VGroup(*[text(nm, 20, GREY_A).next_to(bx.c2p(k + 0.5, 0), DOWN) for k, (nm, _, _) in enumerate(vals)])
        yl = text("compliance (lower is better)", 22, GREY_A).next_to(bx, LEFT).rotate(PI / 2).shift(0.4 * RIGHT)
        self.narrate("On this benchmark, geometry projection did best; moving morphable components and the moving node "
                     "approach both stopped near eighty-four.")
        self.play(Write(hd2), Create(bx), FadeIn(names), FadeIn(yl))
        self.play(LaggedStart(*[GrowFromEdge(c, DOWN) for c in cols], lag_ratio=0.3), FadeIn(nums))
        self.clear_all()


# ================================================================== 16. Evidence, pylon
class S16Pylon(Narrated):
    def construct(self):
        hd = heading("The pylon")
        a = card("simp_pylon", height=3.4).move_to(3.5 * LEFT + 0.9 * UP)
        b = card("mna_pylon", height=3.4).move_to(3.3 * RIGHT + 0.9 * UP)
        la = text("densities (SIMP)", 26, SOLVED).next_to(a, DOWN, buff=0.15)
        lb = text("parts: pylon boxes + cylinder mounts (MNA)", 26, ACCENT).next_to(b, DOWN, buff=0.15)
        ta = VGroup(text("volume 4.97 %", 26), text("delta TSFC 0.159 %   (target 0.16)", 26), text("max stress 30.1 MPa", 26)).arrange(DOWN, aligned_edge=LEFT).next_to(la, DOWN)
        tb = VGroup(text("volume 9.79 %", 26), text("delta TSFC 0.170 %   (target 0.17)", 26), text("max stress 30.1 MPa", 26)).arrange(DOWN, aligned_edge=LEFT).next_to(lb, DOWN)
        self.narrate("On the pylon, the density method found a well-connected structure using five percent of the volume, "
                     "with delta TSFC at zero point one six.")
        self.play(Write(hd), FadeIn(a), FadeIn(la))
        self.play(FadeIn(ta))
        self.narrate("With pylon boxes and cylinder mounts, the solution is close to how pylons are actually built, but "
                     "heavier: nine point eight percent of the volume, at a looser target of zero point one seven.")
        self.play(FadeIn(b), FadeIn(lb))
        self.play(FadeIn(tb))
        cav = text("targets differ: the volumes are not a like-for-like comparison", 22, GREY_B).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(cav))
        same = text("same load path: variants of one architecture", 30, ACCENT).to_edge(DOWN, buff=0.3)
        self.narrate("Different methods, different details, but the same load path: variants of one architecture.")
        self.play(FadeOut(cav), FadeIn(same, shift=UP * 0.2))
        self.clear_all()


# ================================================================== 17. Back to the hook, recap
class S17Recap(Narrated):
    def construct(self):
        P = pareto()
        ax = Axes(x_range=[3.4, 5.2, 0.4], y_range=[0.155, 0.19, 0.01], x_length=5.6, y_length=3.8,
                  axis_config={"color": GREY_B, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": [3.6, 4.0, 4.4, 4.8], "decimal_number_config": {"num_decimal_places": 1}},
                  y_axis_config={"numbers_to_include": [0.16, 0.17, 0.18], "decimal_number_config": {"num_decimal_places": 2}}
                  ).move_to(3.2 * LEFT + 0.6 * DOWN)
        xl = text("volume (%)", 22, GREY_A).next_to(ax.x_axis, DOWN, buff=0.45)
        yl = text("extra fuel (%)", 22, GREY_A).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.55)
        order = ["D", "C", "B", "A"]
        pts = VGroup(*[Dot(ax.c2p(*P[k]), radius=0.09, color=interpolate_color(ManimColor(BAD), ManimColor(GOOD), i / 3)) for i, k in enumerate(order)])
        labs = VGroup(*[text(k, 22).next_to(p, UR, buff=0.08) for k, p in zip(order, pts)])
        line = VMobject(color=GREY_B).set_points_as_corners([p.get_center() for p in pts])
        hd = heading("Back to the two pylons")
        self.narrate("Back to our two pylons. Tightening the target from zero point one eight three to zero point one six "
                     "costs about a third more material, and the four optimized designs show where it goes.")
        self.play(Write(hd), Create(ax), FadeIn(xl), FadeIn(yl))
        self.play(LaggedStart(*[FadeIn(p, scale=2) for p in pts], lag_ratio=0.4), FadeIn(labs), Create(line), run_time=2.5)
        eng = card("engine_labels", height=3.3).move_to(3.6 * RIGHT + 0.8 * UP)
        spot = Circle(0.35, color=ACCENT, stroke_width=6).move_to(eng.get_corner(UL) + np.array([0.446 * eng.width, -0.41 * eng.height, 0]))
        key = text("core casing  ↔  OGV base: stiffened as the target tightens", 22, ACCENT).next_to(eng, DOWN)
        self.narrate("As the target tightens, the front stiffens, in particular the link between the core casing and the "
                     "base of the outlet guide vanes: a key connection for controlling how the engine deforms.")
        self.play(FadeIn(eng))
        self.play(Create(spot), FadeIn(key))
        self.hush()
        self.play(*[FadeOut(m) for m in self.mobjects])
        rec = VGroup(
            text("1.  Fuel burn can sit inside topology optimization, from the first sketch.", 30),
            text("2.  At industrial scale: superelements, mesh tying, filters, relaxation, adjoints.", 30),
            text("3.  With densities for freedom, or with parts unified by GGP, closer to what can be built.", 30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        rec.scale_to_fit_width(min(rec.width, 13))
        t = text("The thesis in three lines", 40, ACCENT).next_to(rec, UP, buff=0.7)
        self.narrate("That's the thesis in three lines.")
        self.play(Write(t))
        self.narrate("One: fuel burn can sit inside topology optimization, from the very first sketch.")
        self.play(FadeIn(rec[0], shift=RIGHT * 0.2))
        self.narrate("Two: at industrial scale, thanks to superelements, mesh tying, filters, relaxation and adjoints.")
        self.play(FadeIn(rec[1], shift=RIGHT * 0.2))
        self.narrate("Three: with densities for freedom, or with parts, unified by the generalized geometry projection, "
                     "for designs closer to what can be built.")
        self.play(FadeIn(rec[2], shift=RIGHT * 0.2))
        self.hush()
        self.wait(1)
        self.clear_all()
        end = VGroup(text("Propulsion Airframe Topology Optimization", 40), text("including engine performance and stress criteria", 28, GREY_A),
                     text("Simone Coniglio · PhD thesis, Université de Toulouse", 24, SOLVED)).arrange(DOWN, buff=0.3)
        self.play(FadeIn(end))
        self.wait(3)
        self.play(FadeOut(end))


SCENES = ["S01Hook", "S02Clearance", "S03Number", "S04Problem", "S05Usual", "S06Simp", "S07Filter", "S08Super",
          "S09Tying", "S10Singular", "S11Relax", "S12Adjoint", "S13Ggp", "S14Beam", "S15Cantilever", "S16Pylon", "S17Recap"]
