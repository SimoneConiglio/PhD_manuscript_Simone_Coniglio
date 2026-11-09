"""The thesis told to a three-year-old: a bright, picture-first version, about 3 minutes.

    VIDEO_LANG=en-us VIDEO_VOICE=af_heart  (English)   or   VIDEO_LANG=fr-fr VIDEO_VOICE=ff_siwis  (French)
    python synth.py kid
    bash <skill>/scripts/render.sh <venv> kid.py out_kid qh
    bash <skill>/scripts/assemble.sh out_kid qh kid.mp4

The building animations replay the real runs of the thesis video (data/simp.npz, data/ggp_repo_GP.npz).
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np
from explainer import Narrated
from manim import *  # noqa: F401,F403

FR = os.environ.get("VIDEO_LANG", "en-us").lower().startswith("fr")
DATA = HERE / "data"
SKY = "#cfeeff"
INK = "#2b2d42"
ORANGE = "#ff9a3c"
RED = "#ef476f"
GREEN = "#06d6a0"
YELLOW_K = "#ffd166"
BLUE_K = "#118ab2"
GREYK = "#8d99ae"
config.background_color = SKY
FONT = "Latin Modern Roman"

SAY = {
    "plane": ("Look! A big airplane!", "Regarde ! Un grand avion !"),
    "engine": ("Under its wing, there is a big engine. Vroom, vroom!", "Sous son aile, il y a un gros moteur. Vroum, vroum !"),
    "pylon": ("The engine is held by an arm. This arm is called a pylon.", "Le moteur est tenu par un bras. Ce bras s'appelle un mât."),
    "fan": ("Inside the engine, a big fan spins round and round, super fast!", "Dans le moteur, un grand ventilateur tourne et tourne, super vite !"),
    "gap": ("The fan must not touch the wall around it. There is a tiny little gap.", "Le ventilateur ne doit pas toucher le mur tout autour. Il y a un tout petit espace."),
    "wobble": ("But when the plane turns, the engine wiggles. Wobble, wobble!", "Mais quand l'avion tourne, le moteur bouge. Gigote, gigote !"),
    "bump": ("Oops! The fan bumps the wall... and air escapes!", "Oups ! Le ventilateur cogne le mur... et l'air s'échappe !"),
    "thirsty": ("Then the engine gets thirsty, and drinks more fuel.", "Alors le moteur a soif, et il boit plus de carburant."),
    "computer": ("So Simone asked a computer to build the best arm.", "Alors Simone a demandé à un ordinateur de construire le meilleur bras."),
    "blocks": ("Like playing with blocks: the computer adds a block here, and takes one away there...", "Comme avec des cubes : l'ordinateur ajoute un cube ici, et en enlève un là..."),
    "again": ("...again and again, until the shape is strong and light!", "...encore et encore, jusqu'à ce que la forme soit solide et légère !"),
    "thin": ("Too thin? Crack! It breaks.", "Trop fin ? Crac ! Il casse."),
    "big": ("Too big? Too heavy! The airplane gets tired.", "Trop gros ? Trop lourd ! L'avion est fatigué."),
    "right": ("Just right! Strong, light, and the engine stays nice and still.", "Juste comme il faut ! Solide, léger, et le moteur reste bien tranquille."),
    "sticks": ("The computer can also play with sticks.", "L'ordinateur peut aussi jouer avec des bâtons."),
    "slide": ("The sticks slide, turn and grow, until they make a strong shape with triangles.", "Les bâtons glissent, tournent et grandissent, jusqu'à faire une forme solide, avec des triangles."),
    "now": ("Now the engine stays still, the fan does not bump, and the airplane uses less fuel.", "Maintenant, le moteur reste tranquille, le ventilateur ne cogne plus, et l'avion consomme moins de carburant."),
    "bye": ("Bye-bye, airplane! See you in the sky!", "Au revoir, l'avion ! À bientôt dans le ciel !"),
}
WORDS = {"Vroom!": "Vroum !", "Bump!": "Bong !", "Crack!": "Crac !", "Bye-bye!": "Au revoir !", "pylon": "mât",
         "Thank you, Simone!": "Merci, Simone !"}


def say(key):
    return SAY[key][1 if FR else 0]


def word(s, size=60, color=INK):
    return Text(WORDS.get(s, s) if FR else s, font=FONT, font_size=size, color=color, weight=BOLD)


def cloud(scale=1.0):
    c = VGroup(*[Circle(r, fill_color=WHITE, fill_opacity=1, stroke_width=0).shift(np.array([x, y, 0]))
                 for r, x, y in ((0.5, 0, 0), (0.65, 0.6, 0.2), (0.5, 1.2, 0), (0.45, 0.6, -0.15))])
    return c.scale(scale)


def plane():
    body = RoundedRectangle(corner_radius=0.65, width=6.4, height=1.3, fill_color=WHITE, fill_opacity=1, stroke_color=INK, stroke_width=4)
    stripe = Rectangle(width=5.4, height=0.18, fill_color=BLUE_K, fill_opacity=1, stroke_width=0).move_to(body).shift(0.15 * DOWN)
    wins = VGroup(*[Circle(0.12, fill_color=BLUE_K, fill_opacity=1, stroke_width=0).move_to(body.get_center() + np.array([x, 0.22, 0]))
                    for x in np.linspace(-1.8, 1.0, 7)])
    tail = Polygon([-3.0, 0.3, 0], [-3.4, 1.7, 0], [-2.5, 1.7, 0], [-1.9, 0.5, 0], fill_color=RED, fill_opacity=1, stroke_color=INK, stroke_width=4)
    eye1 = VGroup(Circle(0.17, fill_color=WHITE, fill_opacity=1, stroke_color=INK, stroke_width=3), Dot(radius=0.07, color=INK).shift(0.04 * RIGHT)).move_to([2.45, 0.25, 0])
    smile = Arc(radius=0.3, start_angle=-PI * 0.85, angle=PI * 0.6, color=INK, stroke_width=4).move_to([2.55, -0.25, 0])
    wing = Polygon([-0.6, -0.1, 0], [0.9, -0.1, 0], [-0.4, -1.0, 0], [-1.6, -1.0, 0], fill_color=GREYK, fill_opacity=1, stroke_color=INK, stroke_width=4)
    eng = RoundedRectangle(corner_radius=0.3, width=1.8, height=0.75, fill_color="#5c6b7a", fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-0.2, -1.75, 0])
    front = Ellipse(width=0.3, height=0.75, fill_color=GREY_D, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to(eng.get_right())
    pylon = Polygon([-0.7, -1.0, 0], [0.2, -1.0, 0], [0.4, -1.38, 0], [-0.8, -1.38, 0], fill_color=ORANGE, fill_opacity=1, stroke_color=INK, stroke_width=3)
    g = VGroup(tail, wing, body, stripe, wins, eye1, smile, pylon, eng, front)
    g.engine, g.pylon = VGroup(eng, front), pylon
    return g


def field_img(values, nelx, nely, width, color=ORANGE, bg=WHITE):
    a = np.clip(np.asarray(values).reshape(nelx, nely).T, 0, 1)[..., None]
    c, b = np.array(ManimColor(color).to_rgb()) * 255, np.array(ManimColor(bg).to_rgb()) * 255
    rgb = (b + (c - b) * a).astype(np.uint8)
    rgba = np.concatenate([rgb, np.full((*rgb.shape[:2], 1), 255, np.uint8)], 2)
    img = ImageMobject(np.repeat(np.repeat(rgba, 6, 0), 6, 1))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    img.width = width
    return img


def fan(center, r=2.0):
    casing = Circle(r + 0.25, stroke_color=INK, stroke_width=14).move_to(center)
    blades = VGroup(*[Polygon(center, center + r * np.array([np.cos(a - 0.12), np.sin(a - 0.12), 0]),
                              center + r * np.array([np.cos(a + 0.12), np.sin(a + 0.12), 0]),
                              fill_color=[BLUE_K, ORANGE][k % 2], fill_opacity=1, stroke_color=INK, stroke_width=2)
                      for k, a in enumerate(np.linspace(0, TAU, 12, endpoint=False))])
    hub = Circle(0.4, fill_color=YELLOW_K, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to(center)
    return casing, VGroup(blades, hub)


class K01Plane(Narrated):
    def construct(self):
        clouds = VGroup(cloud(1.0).move_to([-5, 2.6, 0]), cloud(0.8).move_to([4.5, 2.9, 0]), cloud(1.2).move_to([3, -3, 0]))
        p = plane().move_to(RIGHT * 9)
        self.add(clouds)
        self.narrate(say("plane"))
        self.play(p.animate.move_to(ORIGIN), run_time=3, rate_func=smooth)
        self.play(p.animate.shift(0.2 * UP), rate_func=there_and_back, run_time=1)
        self.hush()
        self.narrate(say("engine"))
        self.play(p.animate.scale(1.6).shift(1.4 * UP + 0.4 * RIGHT), run_time=1.5)
        vroom = word("Vroom!", 72, ORANGE).move_to([3.6, -2.6, 0])
        self.play(Wiggle(p.engine, scale_value=1.15, rotation_angle=0.05 * TAU), FadeIn(vroom, scale=1.5))
        self.play(Wiggle(p.engine, scale_value=1.15, rotation_angle=0.05 * TAU))
        self.hush()
        self.play(FadeOut(vroom))
        lab = word("pylon", 54, ORANGE).move_to([-4.0, -2.8, 0])
        arr = Arrow(lab.get_top(), p.pylon.get_left(), color=ORANGE, stroke_width=8, buff=0.15)
        self.narrate(say("pylon"))
        self.play(Indicate(p.pylon, color=ORANGE, scale_factor=1.5), FadeIn(lab), GrowArrow(arr), run_time=2)
        self.play(Indicate(p.pylon, color=ORANGE, scale_factor=1.5))
        self.clear_all()


class K02Fan(Narrated):
    def construct(self):
        c = ORIGIN
        casing, rotor = fan(c)
        self.narrate(say("fan"))
        self.play(Create(casing), FadeIn(rotor, scale=0.5))
        rotor.add_updater(lambda m, dt: m.rotate(4 * dt, about_point=c))
        self.wait(3)
        self.hush()
        ring = Annulus(inner_radius=2.0, outer_radius=2.18, fill_color=YELLOW_K, fill_opacity=0.9, stroke_width=0).move_to(c)
        self.narrate(say("gap"))
        self.play(FadeIn(ring))
        self.play(ring.animate.set_opacity(0.2), rate_func=there_and_back, run_time=1)
        self.play(ring.animate.set_opacity(0.2), rate_func=there_and_back, run_time=1)
        self.hush()
        rotor.clear_updaters()
        self.clear_all()


class K03Wobble(Narrated):
    def construct(self):
        c = 2.5 * LEFT
        casing, rotor = fan(c, r=1.9)
        rotor.add_updater(lambda m, dt: m.rotate(4 * dt, about_point=rotor[1].get_center()))
        self.add(casing, rotor)
        self.narrate(say("wobble"))
        for k in range(3):
            self.play(casing.animate.shift(0.25 * DOWN).rotate(0.08), run_time=0.4)
            self.play(casing.animate.shift(0.25 * UP).rotate(-0.08), run_time=0.4)
        self.hush()
        self.narrate(say("bump"))
        self.play(casing.animate.shift(0.3 * DOWN), run_time=0.4)
        hit = rotor[1].get_center() + 2.0 * UP
        star = Star(7, outer_radius=0.6, inner_radius=0.3, fill_color=YELLOW_K, fill_opacity=1, stroke_color=INK).move_to(hit)
        bump = word("Bump!", 60, RED).next_to(star, UP)
        self.play(FadeIn(star, scale=2), FadeIn(bump), Flash(hit, color=RED, flash_radius=0.8))
        puffs = VGroup(*[Circle(0.18, fill_color=WHITE, fill_opacity=0.9, stroke_width=0).move_to(rotor[1].get_center() + 2.3 * DOWN + 0.4 * k * RIGHT) for k in range(-2, 3)])
        self.play(LaggedStart(*[p.animate.shift(1.2 * DOWN + 0.3 * RIGHT * (k - 2)).set_opacity(0) for k, p in enumerate(puffs)], lag_ratio=0.15), run_time=1.5)
        self.hush()
        tank = RoundedRectangle(corner_radius=0.2, width=1.6, height=3.0, stroke_color=INK, stroke_width=6).move_to(3.8 * RIGHT + 0.2 * DOWN)
        level = ValueTracker(2.8)
        fuel = always_redraw(lambda: Rectangle(width=1.4, height=max(level.get_value(), 0.01), fill_color=ORANGE, fill_opacity=1,
                                               stroke_width=0).align_to(tank, DOWN).shift(0.1 * UP).set_x(tank.get_x()))
        drop = VGroup(Circle(0.35, fill_color=ORANGE, fill_opacity=1, stroke_width=0),
                      Triangle(fill_color=ORANGE, fill_opacity=1, stroke_width=0).scale(0.37).shift(0.33 * UP)).next_to(tank, UP)
        self.narrate(say("thirsty"))
        self.play(Create(tank), FadeIn(fuel), FadeIn(drop))
        self.play(level.animate.set_value(0.6), run_time=2.5)
        rotor.clear_updaters()
        self.clear_all()


class K04Blocks(Narrated):
    def construct(self):
        screen = RoundedRectangle(corner_radius=0.3, width=8.4, height=4.8, fill_color=INK, fill_opacity=1, stroke_width=0).shift(0.4 * UP)
        stand = VGroup(Rectangle(width=0.6, height=0.8, fill_color=INK, fill_opacity=1, stroke_width=0).next_to(screen, DOWN, buff=0),
                       RoundedRectangle(corner_radius=0.1, width=3, height=0.3, fill_color=INK, fill_opacity=1, stroke_width=0).next_to(screen, DOWN, buff=0.8))
        smile = VGroup(Dot([-0.8, 0.9, 0], radius=0.18, color=WHITE), Dot([0.8, 0.9, 0], radius=0.18, color=WHITE),
                       Arc(radius=0.8, start_angle=-PI * 0.8, angle=PI * 0.6, color=WHITE, stroke_width=8).move_to([0, 0.0, 0]))
        self.narrate(say("computer"))
        self.play(FadeIn(screen), FadeIn(stand))
        self.play(FadeIn(smile), run_time=1)
        self.hush()
        self.play(FadeOut(smile))
        hist = np.load(DATA / "simp.npz")["hist"]
        it = ValueTracker(0)
        img = always_redraw(lambda: field_img(hist[int(it.get_value())], 60, 30, 7.6).move_to(screen))
        self.add(img)
        self.narrate(say("blocks"))
        self.play(it.animate.set_value(30), run_time=5, rate_func=linear)
        self.narrate(say("again"))
        self.play(it.animate.set_value(len(hist) - 1), run_time=4)
        star = Star(5, outer_radius=0.7, inner_radius=0.3, fill_color=YELLOW_K, fill_opacity=1, stroke_color=INK).next_to(screen, RIGHT, buff=-0.2).shift(1.8 * UP)
        self.play(FadeIn(star, scale=2), Rotate(star, TAU / 5))
        self.clear_all()


class K05JustRight(Narrated):
    def construct(self):
        xs = (-4.6, 0, 4.6)
        walls = VGroup(*[Rectangle(width=0.3, height=2.6, fill_color=GREYK, fill_opacity=1, stroke_width=0).move_to([x - 1.6, 0.3, 0]) for x in xs])
        engines = VGroup(*[Circle(0.45, fill_color="#5c6b7a", fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x + 1.5, -0.3, 0]) for x in xs])
        self.add(walls, engines)
        thin = Line([xs[0] - 1.45, 0.3, 0], [xs[0] + 1.1, -0.2, 0], color=ORANGE, stroke_width=4)
        self.narrate(say("thin"))
        self.play(Create(thin))
        left = Line(thin.get_start(), thin.point_from_proportion(0.5), color=ORANGE, stroke_width=4)
        right = Line(thin.point_from_proportion(0.5), thin.get_end(), color=ORANGE, stroke_width=4)
        crack = word("Crack!", 50, RED).move_to([xs[0], 2.3, 0])
        self.remove(thin)
        self.add(left, right)
        self.play(FadeIn(crack, scale=1.5), Rotate(right, -0.6, about_point=right.get_start()), engines[0].animate.shift(1.2 * DOWN), run_time=1)
        cross = Cross(VGroup(left, right, engines[0]), stroke_color=RED, stroke_width=8)
        self.play(Create(cross))
        self.hush()
        big = Rectangle(width=3.0, height=2.4, fill_color=ORANGE, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([xs[1], 0.0, 0])
        weight = VGroup(Polygon([-0.6, -0.4, 0], [0.6, -0.4, 0], [0.4, 0.4, 0], [-0.4, 0.4, 0], fill_color=INK, fill_opacity=1, stroke_width=0),
                        Text("kg", font=FONT, font_size=30, color=WHITE)).move_to([xs[1], -2.2, 0])
        self.narrate(say("big"))
        self.play(GrowFromCenter(big))
        self.play(FadeIn(weight, shift=DOWN), big.animate.shift(0.3 * DOWN), engines[1].animate.shift(0.3 * DOWN))
        self.hush()
        a = np.load(DATA / "simp.npz")["hist"][-1]
        truss = field_img(a, 60, 30, 3.0, color=GREEN, bg=SKY).move_to([xs[2], 0.0, 0])
        check = VGroup(Star(5, outer_radius=0.5, inner_radius=0.22, fill_color=YELLOW_K, fill_opacity=1, stroke_color=INK).move_to([xs[2], 2.3, 0]))
        self.narrate(say("right"))
        self.play(FadeIn(truss, scale=0.5))
        self.play(FadeIn(check, scale=2), truss.animate.scale(1.12), rate_func=there_and_back)
        self.clear_all()


class K06Sticks(Narrated):
    def construct(self):
        d = np.load(DATA / "ggp_repo_GP.npz")
        comps = d["comps"]
        N = len(comps) - 1
        W = 9.0
        cs = W / 60
        frame = Rectangle(width=W, height=W / 2, fill_color=WHITE, fill_opacity=1, stroke_color=INK, stroke_width=6).shift(0.2 * DOWN)
        org = frame.get_corner(DL)
        it = ValueTracker(0)
        palette = [ORANGE, BLUE_K, RED, GREEN, "#9b5de5", YELLOW_K]

        def sticks():
            g = VGroup()
            for k, (x0, y0, L, h, t, m) in enumerate(comps[int(it.get_value())]):
                w = float(m) ** 3
                if w < 0.05:
                    continue
                h = max(h, 0.3)
                g.add(RoundedRectangle(corner_radius=h * cs / 2 * 0.999, width=(L + h) * cs, height=h * cs, fill_color=palette[k % 6],
                                       fill_opacity=0.85 * w, stroke_color=INK, stroke_width=2, stroke_opacity=w)
                      .rotate(t).move_to(org + np.array([x0 * cs, y0 * cs, 0])))
            return g

        st = always_redraw(sticks)
        masks = VGroup(*[Rectangle(width=30, height=30).next_to(frame, dr, buff=0) for dr in (LEFT, RIGHT, UP, DOWN)]).set_style(
            fill_color=SKY, fill_opacity=1, stroke_width=0)
        wall = Rectangle(width=0.3, height=W / 2 + 0.4, fill_color=GREYK, fill_opacity=1, stroke_width=0).next_to(frame, LEFT, buff=0)
        eng = Circle(0.45, fill_color="#5c6b7a", fill_opacity=1, stroke_color=INK, stroke_width=4).next_to(frame, RIGHT, buff=0.1)
        self.add(frame, st, masks)
        self.narrate(say("sticks"))
        self.play(FadeIn(wall), FadeIn(eng), Create(frame.copy().set_fill(opacity=0)), run_time=1.5)
        self.hush()
        self.narrate(say("slide"))
        self.play(it.animate.set_value(N), run_time=9, rate_func=lambda s: s ** 0.8)
        star = Star(5, outer_radius=0.6, inner_radius=0.26, fill_color=YELLOW_K, fill_opacity=1, stroke_color=INK).next_to(frame, UP, buff=0.1)
        self.play(FadeIn(star, scale=2))
        self.hush()
        self.remove(st)
        self.clear_all()


class K07Bye(Narrated):
    def construct(self):
        clouds = VGroup(cloud(1.0).move_to([-5, 2.6, 0]), cloud(0.8).move_to([4.5, 2.9, 0]), cloud(1.2).move_to([3, -3, 0]))
        p = plane().scale(1.2)
        p.pylon.set_fill(GREEN)
        self.add(clouds)
        self.narrate(say("now"))
        self.play(FadeIn(p, shift=LEFT))
        self.play(Indicate(p.pylon, color=GREEN, scale_factor=1.6), run_time=1.5)
        self.play(clouds.animate.shift(2 * LEFT), run_time=3, rate_func=linear)
        self.hush()
        bye = word("Bye-bye!", 80, ORANGE).shift(2.6 * DOWN)
        self.narrate(say("bye"))
        self.play(p.animate.shift(10 * RIGHT + 2 * UP).scale(0.4), FadeIn(bye, scale=1.4), run_time=3)
        self.hush()
        self.play(FadeOut(bye))
        end = word("Thank you, Simone!", 64, INK)
        self.play(FadeIn(end, scale=1.2))
        self.wait(2.5)
        self.play(FadeOut(end), FadeOut(clouds))


SCENES = ["K01Plane", "K02Fan", "K03Wobble", "K04Blocks", "K05JustRight", "K06Sticks", "K07Bye"]
