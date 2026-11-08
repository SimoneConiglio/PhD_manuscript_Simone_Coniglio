"""
Explainer video for the PhD thesis
"Propulsion Airframe Topology Optimization including engine performance
and stress criteria" -- Simone Coniglio.

Built with Manim Community (the community edition of 3Blue1Brown's library).

Render everything with:   ./render.sh          (see README.md)
Optimization histories: topopt_data.py (SIMP) and run_ggp_repo.py (GGP-Python, thesis settings).
"""
from manim import *
import numpy as np
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "Phd_SC", "images")
DATA = os.path.join(HERE, "data")

config.background_color = "#0f1117"
MAT = np.array([88, 196, 221])      # material colour (3b1b blue)
BG = np.array([15, 17, 23])
ACCENT = YELLOW
NELX, NELY = 60, 30


# ---------------------------------------------------------------- helpers
def caption(text, scale=0.42):
    t = Text(text, font_size=48, line_spacing=0.9).scale(scale)
    t.to_edge(DOWN, buff=0.35)
    return t


def chapter_card(scene, number, title, subtitle=None):
    n = Text(number, font_size=30, color=GREY_B)
    t = Text(title, font_size=52, weight=BOLD)
    g = VGroup(n, t).arrange(DOWN, buff=0.3)
    if subtitle:
        s = Text(subtitle, font_size=28, color=BLUE_B)
        g.add(s)
        g.arrange(DOWN, buff=0.3)
    line = Line(LEFT * 3, RIGHT * 3, color=BLUE).next_to(t, DOWN, buff=0.15)
    scene.play(FadeIn(n, shift=DOWN * 0.2), Write(t), run_time=1.2)
    scene.play(Create(line), *([FadeIn(g[2])] if subtitle else []), run_time=0.8)
    scene.wait(1.2)
    scene.play(FadeOut(VGroup(g, line)))


def density_image(field, width):
    """field: (NELX*NELY,) element densities in thesis/top88 ordering."""
    arr = np.clip(field.reshape(NELX, NELY).T, 0, 1)[..., None]
    rgb = (BG + (MAT - BG) * arr).astype(np.uint8)
    rgba = np.concatenate([rgb, 255 * np.ones((*rgb.shape[:2], 1), np.uint8)], axis=2)
    rgba = np.repeat(np.repeat(rgba, 8, axis=0), 8, axis=1)
    img = ImageMobject(rgba)
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    img.width = width
    return img


def thesis_image(rel, height):
    """White-background thesis figure placed on a rounded card."""
    im = ImageMobject(os.path.join(IMG, rel))
    im.height = height
    card = RoundedRectangle(corner_radius=0.15, width=im.width + 0.3,
                            height=im.height + 0.3, fill_color=WHITE,
                            fill_opacity=1, stroke_width=0)
    return Group(card, im)


def clear(scene, run_time=0.8):
    scene.play(*[FadeOut(m) for m in scene.mobjects], run_time=run_time)


# ================================================================ 1. Intro
class S1_Intro(Scene):
    def construct(self):
        title = Text("Propulsion Airframe Topology Optimization", font_size=44, weight=BOLD)
        sub = Text("including engine performance and stress criteria", font_size=32, color=BLUE_B)
        who = Text("PhD thesis  ·  Simone Coniglio  ·  Université de Toulouse", font_size=24, color=GREY_B)
        VGroup(title, sub, who).arrange(DOWN, buff=0.35)
        self.play(Write(title), run_time=2)
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.play(FadeIn(who))
        self.wait(2)
        clear(self)

        # --- CO2 context
        q = Text("Why does this matter?", font_size=40).to_edge(UP)
        self.play(Write(q))
        bar_ax = BarChart(values=[98, 2], bar_names=["Everything else", "Aviation"],
                          y_range=[0, 100, 25], y_length=3.5, x_length=4.5,
                          bar_colors=[GREY_C, ACCENT]).shift(LEFT * 3 + DOWN * 0.3)
        lbl = Text("share of human CO₂", font_size=22, color=GREY_B).next_to(bar_ax, DOWN)
        self.play(Create(bar_ax), FadeIn(lbl))
        pts = VGroup(
            Text("• Aviation ≈ 2% of CO₂ emissions — and growing", font_size=26),
            Text("• > 90% of it comes from large single/twin-aisle jets", font_size=26),
            Text("• Their engines: turbofans hung under the wing by a pylon", font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        pts.scale_to_fit_width(7.2).next_to(bar_ax, RIGHT, buff=0.6)
        for p in pts:
            self.play(FadeIn(p, shift=RIGHT * 0.2), run_time=0.8)
            self.wait(1.2)
        self.wait(1)
        clear(self)

        # --- UHBR engines: bigger fan, thinner core
        t = Text("The trend: Ultra-High Bypass Ratio engines", font_size=36).to_edge(UP)
        self.play(Write(t))
        fan = Rectangle(width=0.6, height=2.4, color=BLUE, fill_opacity=0.3)
        core = Rectangle(width=3.0, height=1.0, color=GREY_B, fill_opacity=0.3).next_to(fan, RIGHT, buff=0)
        engine = VGroup(fan, core).move_to(ORIGIN)
        self.play(Create(engine))
        self.play(fan.animate.stretch_to_fit_height(3.6),
                  core.animate.stretch_to_fit_height(0.7), run_time=2)
        a = Text("larger fan", font_size=24, color=BLUE).next_to(fan, LEFT)
        b = Text("slimmer, more flexible core", font_size=24, color=GREY_B).next_to(core, DOWN, buff=0.9)
        self.play(FadeIn(a), FadeIn(b))
        self.play(engine.animate.apply_function(
            lambda p: p + np.array([0, -0.12 * (p[0] + 0.5) ** 2 * (p[0] > -0.5), 0])), run_time=2)
        self.add(caption("More efficient on paper… but the engine bends more under flight loads."))
        self.wait(3)
        clear(self)


# ================================================================ 2. Tip clearance
class S2_TipClearance(Scene):
    def construct(self):
        chapter_card(self, "The problem", "Tip clearance")
        R, r = 2.3, 2.0
        center = LEFT * 3
        oval = ValueTracker(0.0)

        def casing():
            a = oval.get_value()
            return ParametricFunction(
                lambda t: center + np.array([(R + a * 0.18) * np.cos(t),
                                             (R - a * 0.18) * np.sin(t) - a * 0.17, 0]),
                t_range=[0, TAU], color=GREY_A, stroke_width=6)

        cas = always_redraw(casing)
        hub = Circle(radius=0.5, color=BLUE_D, fill_opacity=0.5).move_to(center)
        blades = VGroup(*[Line(center + 0.5 * np.array([np.cos(t), np.sin(t), 0]),
                               center + r * np.array([np.cos(t), np.sin(t), 0]),
                               color=BLUE_B, stroke_width=4)
                          for t in np.linspace(0, TAU, 24, endpoint=False)])
        rotor = VGroup(hub, blades)
        self.play(Create(cas), FadeIn(rotor))
        self.play(Rotate(rotor, PI / 2, about_point=center), run_time=1.5)

        zoom = Brace(Line(center + UP * r, center + UP * R), RIGHT, color=ACCENT)
        lab = Text("tip clearance", font_size=26, color=ACCENT).next_to(zoom, RIGHT)
        self.play(GrowFromCenter(zoom), FadeIn(lab))
        txt = VGroup(
            Text("Gap between rotating blade tips", font_size=26),
            Text("and the fixed engine casing", font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT).shift(UP * 2)
        self.play(FadeIn(txt))
        self.wait(1.5)
        self.play(FadeOut(zoom), FadeOut(lab))

        # flight loads deform the casing
        arrow = Arrow(center + UP * 3.6, center + UP * 2.5, color=RED, buff=0)
        fl = Text("manoeuvre loads", font_size=22, color=RED).next_to(arrow, RIGHT)
        self.play(GrowArrow(arrow), FadeIn(fl))
        self.play(oval.animate.set_value(1.0), run_time=2.5)
        rub = Dot(center + DOWN * (r + 0.02), color=RED, radius=0.12)
        self.play(Flash(rub, color=RED, flash_radius=0.4), FadeIn(rub))
        pts = VGroup(
            Text("Gap closes → blades rub the casing", font_size=24),
            Text("Gap opens → air leaks over the tips", font_size=24),
            Text("Either way: higher fuel consumption", font_size=24, color=ACCENT),
            MathTex(r"\Delta \mathrm{TSFC}\,\% \uparrow", color=ACCENT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(txt, DOWN, buff=0.6).align_to(txt, LEFT)
        for p in pts:
            self.play(FadeIn(p, shift=RIGHT * 0.2), run_time=0.7)
            self.wait(0.8)
        self.wait(2)
        clear(self)

        # --- side view: wing, pylon, engine, design space
        wing = Polygon([-6, 3, 0], [6, 3, 0], [6, 2.4, 0], [-6, 2.2, 0],
                       color=GREY_B, fill_opacity=0.4)
        eng = VGroup(
            RoundedRectangle(corner_radius=0.3, width=1.0, height=3.0, color=BLUE, fill_opacity=0.3),
            Rectangle(width=4.0, height=1.0, color=BLUE_D, fill_opacity=0.3),
        )
        eng[1].next_to(eng[0], RIGHT, buff=0)
        eng.move_to(DOWN * 1.2 + LEFT * 0.5)
        ds = Rectangle(width=4.0, height=1.9, color=ACCENT, fill_opacity=0.12).move_to(UP * 1.2 + RIGHT * 0.5)
        dsl = Text("design space", font_size=24, color=ACCENT).move_to(ds)
        self.play(FadeIn(wing), FadeIn(eng))
        self.play(Create(ds), Write(dsl))
        self.play(VGroup(wing, eng, ds, dsl).animate.scale(0.72).shift(UP * 0.6))
        lines = VGroup(
            Text("The aircraft maker cannot redesign the engine…", font_size=28),
            Text("…but it controls pylon, engine mounts and nacelle,", font_size=28),
            Text("which change how the engine deforms.", font_size=28, color=ACCENT),
        ).arrange(DOWN, buff=0.15).to_edge(DOWN, buff=0.3)
        for l in lines:
            self.play(FadeIn(l), run_time=0.8)
            self.wait(1.2)
        q = Text("?", font_size=90, color=ACCENT).move_to(ds)
        self.play(ReplacementTransform(dsl, q))
        self.wait(1)
        self.play(FadeOut(lines))
        goal = VGroup(
            Text("Goal: find the best material layout in this box", font_size=30),
            Text("→ Topology Optimization", font_size=34, color=ACCENT, weight=BOLD),
        ).arrange(DOWN).to_edge(DOWN, buff=0.4)
        self.play(Write(goal), run_time=2)
        self.wait(2.5)
        clear(self)

        # --- roadmap
        road = VGroup(
            Text("1. Analyse: a fast, faithful finite element model", font_size=30),
            Text("2. Eulerian topology optimization (density / SIMP)", font_size=30),
            Text("3. Lagrangian topology optimization (moving components)", font_size=30),
            Text("4. Application to the pylon & engine mounts", font_size=30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        hdr = Text("Roadmap of the thesis", font_size=40, weight=BOLD).to_edge(UP)
        self.play(Write(hdr))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in road], lag_ratio=0.4), run_time=3)
        self.wait(3)
        clear(self)


# ================================================================ 3. FEM
class S3_FEM(Scene):
    def construct(self):
        chapter_card(self, "Chapter 1", "Structural analysis by FEM")
        eq = MathTex(r"[K(x)]\,\{U(x)\} = \{F\}", font_size=60)
        self.play(Write(eq))
        expl = VGroup(
            MathTex(r"K", r"\;:\;\text{stiffness (depends on the design } x)", font_size=34),
            MathTex(r"U", r"\;:\;\text{displacements} \;\Rightarrow\; \text{tip clearance, stress}", font_size=34),
            MathTex(r"F", r"\;:\;\text{flight \& manoeuvre loads}", font_size=34),
        ).arrange(DOWN, aligned_edge=LEFT).next_to(eq, DOWN, buff=0.6)
        for e in expl:
            e[0].set_color(ACCENT)
        self.play(FadeIn(expl, shift=UP * 0.2))
        self.add(caption("Every design evaluated during optimization needs this solve — thousands of times."))
        self.wait(3)
        clear(self)

        # --- superelement
        hdr = Text("Challenge 1 · the engine model is industrial", font_size=34).to_edge(UP)
        self.play(Write(hdr))
        pts = np.array([[np.cos(t), np.sin(t)] for t in np.linspace(0, TAU, 14, endpoint=False)])
        rng = np.random.default_rng(1)
        inner = rng.uniform(-0.75, 0.75, (40, 2))
        inner = inner[np.linalg.norm(inner, axis=1) < 0.8]
        scale = 1.6
        bd = VGroup(*[Dot([*(scale * p), 0], color=ACCENT, radius=0.07) for p in pts])
        ind = VGroup(*[Dot([*(scale * p), 0], color=BLUE_C, radius=0.05) for p in inner])
        edges = VGroup(*[Line([*(scale * pts[i]), 0], [*(scale * inner[j]), 0], stroke_width=1, color=GREY_D)
                         for i in range(len(pts)) for j in range(len(inner))
                         if np.linalg.norm(pts[i] - inner[j]) < 0.55])
        model = VGroup(edges, ind, bd).shift(LEFT * 3.5)
        lab = Text("Whole Engine Model\n(Nastran / Abaqus)", font_size=22, color=GREY_B).next_to(model, DOWN)
        self.play(FadeIn(model), FadeIn(lab))
        cond = MathTex(r"K_{SE} = K_{bb} - K_{bi}\,K_{ii}^{-1}\,K_{ib}", font_size=40).shift(RIGHT * 2.8 + UP * 0.8)
        self.play(Write(cond))
        self.play(FadeOut(ind), FadeOut(edges), run_time=1.5)
        se_lab = Text("Superelement: only the\ninterface DOFs remain", font_size=26, color=ACCENT).next_to(cond, DOWN, buff=0.5)
        self.play(FadeIn(se_lab))
        self.add(caption("Same accuracy as the full engine, far fewer unknowns, and tip clearance can still be post-processed."))
        self.wait(4)
        clear(self)

        # --- non-matching meshes
        hdr = Text("Challenge 2 · engine and design-space meshes do not match", font_size=32).to_edge(UP)
        self.play(Write(hdr))
        left = VGroup(*[Square(0.7, stroke_color=BLUE_C).move_to([-1.05 - 0.7 * i, 1.4 - 0.7 * j, 0])
                        for i in range(3) for j in range(5)])
        right = VGroup(*[Square(0.4667, stroke_color=ACCENT).move_to([-0.35 + 0.2333 + 0.4667 * i, 1.75 - 0.2333 - 0.4667 * j, 0])
                         for i in range(4) for j in range(8)])
        right.align_to(left, UP)
        VGroup(left, right).move_to(LEFT * 4.2 + DOWN * 0.2)
        self.play(Create(left), Create(right), run_time=2)
        iface = Line(left.get_corner(UR) + RIGHT * 0.0, left.get_corner(DR), color=RED, stroke_width=6)
        iface.move_to([(left.get_right()[0] + right.get_left()[0]) / 2, left.get_center()[1], 0])
        self.play(Create(iface))
        ln = VGroup(
            Text("Tying techniques implemented and compared:", font_size=26),
            Text("Mortar · Internodes · RL-RBF", font_size=26, color=BLUE_B),
            Text("New: Weighted Average Continuity Approach", font_size=26, color=ACCENT),
            Text("      + moment correction", font_size=26, color=ACCENT),
        ).arrange(DOWN, aligned_edge=LEFT)
        ln.scale_to_fit_width(6.3).move_to(RIGHT * 2.6 + DOWN * 0.2)
        self.play(FadeIn(ln, shift=LEFT * 0.2))
        self.wait(3.5)
        clear(self)

        # --- solver
        hdr = Text("Challenge 3 · millions of unknowns", font_size=34).to_edge(UP)
        self.play(Write(hdr))
        ax = Axes(x_range=[0, 30, 10], y_range=[-8, 0, 2], x_length=6, y_length=3.5,
                  axis_config={"include_numbers": True, "font_size": 20}).shift(LEFT * 2.3 + DOWN * 0.3)
        xl = Text("iterations", font_size=20).next_to(ax.x_axis, DOWN)
        yl = MathTex(r"\log_{10}\|r\|", font_size=26).next_to(ax.y_axis, LEFT)
        cg = ax.plot(lambda k: -8 * k / 300 * 10 / 10, x_range=[0, 30], color=GREY_B)
        mg = ax.plot(lambda k: max(-8, -0.6 * k), x_range=[0, 30], color=ACCENT)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        self.play(Create(cg), run_time=1.5)
        self.play(Create(mg), run_time=1.5)
        leg = VGroup(Text("plain CG", font_size=22, color=GREY_B),
                     Text("multigrid-preconditioned CG", font_size=22, color=ACCENT)
                     ).arrange(DOWN, aligned_edge=LEFT).next_to(ax, RIGHT, buff=0.4).shift(UP)
        self.play(FadeIn(leg))
        self.add(caption("Iterative solvers with multigrid preconditioners and tuned smoothers (schematic curves)."))
        self.wait(3.5)
        clear(self)


# ================================================================ 4. SIMP
class S4_SIMP(Scene):
    def construct(self):
        chapter_card(self, "Chapter 2", "Eulerian Topology Optimization", "density-based · SIMP")
        hdr = Text("Each element gets a density  x ∈ [0, 1]", font_size=34).to_edge(UP)
        self.play(Write(hdr))
        rng = np.random.default_rng(0)
        field = rng.uniform(0, 1, NELX * NELY)
        img = density_image(field, 7)
        self.play(FadeIn(img))
        l0 = Text("0 = void", font_size=24).next_to(img, DOWN).shift(LEFT * 2)
        l1 = Text("1 = solid", font_size=24, color=BLUE_B).next_to(img, DOWN).shift(RIGHT * 2)
        self.play(FadeIn(l0), FadeIn(l1))
        self.wait(2)
        self.play(FadeOut(img), FadeOut(l0), FadeOut(l1))

        # penalization
        p = ValueTracker(1.0)
        ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 0.5], x_length=4.5, y_length=3.5,
                  axis_config={"include_numbers": True, "font_size": 20}).shift(LEFT * 3 + DOWN * 0.4)
        xl = MathTex("x", font_size=30).next_to(ax.x_axis, RIGHT)
        yl = MathTex("E(x)/E", font_size=30).next_to(ax.y_axis, UP)
        curve = always_redraw(lambda: ax.plot(lambda x: x ** p.get_value(), x_range=[0, 1], color=ACCENT))
        eq = MathTex(r"E(x) = E_{min} + (E - E_{min})\,x^{p}", font_size=40).shift(RIGHT * 2.8 + UP * 1.3)
        pv = always_redraw(lambda: MathTex(f"p = {p.get_value():.1f}", font_size=40, color=ACCENT).next_to(eq, DOWN))
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), Create(curve), Write(eq), FadeIn(pv))
        self.play(p.animate.set_value(3.0), run_time=3)
        expl = Text("Grey (intermediate) material gives little\nstiffness for its weight → pushed to 0 or 1",
                    font_size=24).next_to(pv, DOWN, buff=0.5)
        self.play(FadeIn(expl))
        self.wait(3)
        clear(self)

        # formulation
        prob = MathTex(r"\min_{0\le x\le 1}\; c(x) = U^T K(x)\, U", r"\quad\text{s.t.}\quad",
                       r"\frac{V(x)}{V_0} \le v_f", font_size=42).to_edge(UP, buff=0.8)
        self.play(Write(prob))
        filt = MathTex(r"x_{phys}(X) = \int_\Omega \kappa(X,\bar X)\,x(\bar X)\,d\bar X",
                       font_size=36).next_to(prob, DOWN, buff=0.4)
        fl = Text("density filter: removes checkerboards and mesh dependence", font_size=22, color=GREY_B).next_to(filt, DOWN, buff=0.15)
        self.play(FadeIn(filt), FadeIn(fl))
        self.wait(2.5)
        self.play(FadeOut(filt), FadeOut(fl))
        mg = Text("thesis: multigrid strategy to build the filter matrix cheaply on large meshes",
                  font_size=22, color=ACCENT).next_to(prob, DOWN, buff=0.3)
        self.play(FadeIn(mg))
        self.wait(2)
        self.play(FadeOut(mg))

        # live run
        d = np.load(os.path.join(DATA, "simp.npz"))
        hist, comp = d["hist"], d["comp"]
        N = len(hist) - 1
        W = 6.4
        frame = Rectangle(width=W, height=W / 2, color=GREY_B).shift(LEFT * 2.6 + DOWN * 0.8)
        wall = VGroup(*[Line(frame.get_corner(UL) + DOWN * k * 0.32 + LEFT * 0.0,
                             frame.get_corner(UL) + DOWN * k * 0.32 + LEFT * 0.25 + DOWN * 0.2,
                             color=GREY_B) for k in range(11)])
        load = Arrow(frame.get_right() + UP * 0.9, frame.get_right(), color=RED, buff=0)
        it = ValueTracker(0)
        img = always_redraw(lambda: density_image(hist[int(it.get_value())], W).move_to(frame))
        self.add(img)
        self.play(FadeIn(frame), FadeIn(wall), GrowArrow(load))
        ax = Axes(x_range=[0, N, 20], y_range=[0, 300, 100], x_length=4.2, y_length=3,
                  axis_config={"include_numbers": True, "font_size": 18}).shift(RIGHT * 4.3 + DOWN * 0.8)
        axl = Text("compliance", font_size=20).next_to(ax, UP)
        graph = always_redraw(lambda: ax.plot_line_graph(
            np.arange(int(it.get_value()) + 1), np.minimum(comp[:int(it.get_value()) + 1], 300),
            add_vertex_dots=False, line_color=ACCENT, stroke_width=3))
        counter = always_redraw(lambda: Text(f"iteration {int(it.get_value()):3d}", font_size=24)
                                .next_to(frame, UP).align_to(frame, LEFT))
        self.play(Create(ax), FadeIn(axl), FadeIn(counter))
        self.add(graph)
        self.add(caption("A real run (60×30 elements, 40% volume, p = 3, density filter): the load path emerges."))
        self.play(it.animate.set_value(N), run_time=10, rate_func=lambda t: t ** 1.6)
        self.wait(3)
        clear(self)


# ================================================================ 5. Stress
class S5_Stress(Scene):
    def construct(self):
        hdr = Text("Stiff is not enough: the part must not break", font_size=34).to_edge(UP)
        self.play(Write(hdr))
        vm = MathTex(r"\sigma_{VM} = \sqrt{\sigma_{xx}^2 + \sigma_{yy}^2 - \sigma_{xx}\sigma_{yy} + 3\tau_{xy}^2}", font_size=40)
        self.play(Write(vm))
        self.wait(1.5)
        prob = MathTex(r"\min_{x}\; V(x)\quad \text{s.t.}\quad (\sigma_{VM})_i \le \sigma_{lim}\quad \forall i",
                       font_size=40).next_to(vm, DOWN, buff=0.6)
        self.play(Write(prob))
        self.wait(1.5)
        self.play(FadeOut(vm), prob.animate.next_to(hdr, DOWN, buff=0.4))

        c1 = Text("Difficulty 1: singular optima", font_size=28, color=RED_B)
        c2 = Text("Difficulty 2: one constraint per Gauss point (millions!)", font_size=28, color=RED_B)
        VGroup(c1, c2).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(prob, DOWN, buff=0.5)
        self.play(FadeIn(c1))
        self.play(FadeIn(c2))
        self.wait(1.5)

        # many dots -> one
        rng = np.random.default_rng(2)
        dots = VGroup(*[Dot([x, y, 0], radius=0.04, color=interpolate_color(BLUE, RED, rng.uniform()))
                        for x, y in zip(rng.uniform(-5, 5, 250), rng.uniform(-3.3, -1.2, 250))])
        self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.005), run_time=1.5)
        sol = Text("Unified Aggregation & Relaxation", font_size=30, color=ACCENT, weight=BOLD)
        relax = MathTex(r"\bar g_i = x_i\left(\frac{\hat\sigma_{VM,i}}{\sigma_{lim}} - 1\right)", font_size=36)
        agg = MathTex(r"G_{KS} = \frac{1}{P}\log\Big(\frac{1}{N}\sum_i e^{P\,\bar g_i}\Big)\le 0", font_size=36)
        target = Dot([0, -2.3, 0], radius=0.18, color=ACCENT)
        self.play(FadeOut(c1), FadeOut(c2))
        sol.next_to(prob, DOWN, buff=0.4)
        self.play(Write(sol))
        VGroup(relax, agg).arrange(RIGHT, buff=0.8).next_to(sol, DOWN, buff=0.3)
        self.play(FadeIn(relax))
        self.play(FadeIn(agg))
        self.play(*[d.animate.move_to(target) for d in dots], run_time=2)
        self.play(FadeOut(dots), FadeIn(target))
        self.add(caption("Relaxation makes singular optima reachable; aggregation turns millions of constraints into a few."))
        self.wait(4)
        clear(self)

        # adjoint
        hdr = Text("Gradients for free: the adjoint method", font_size=34).to_edge(UP)
        self.play(Write(hdr))
        a1 = MathTex(r"K\,\lambda = \frac{\partial O}{\partial U}", font_size=44)
        a2 = MathTex(r"\frac{dO}{dx_e} = \frac{\partial O}{\partial x_e} - \lambda^T\frac{\partial K}{\partial x_e}U", font_size=44)
        VGroup(a1, a2).arrange(DOWN, buff=0.6)
        self.play(Write(a1))
        self.play(Write(a2))
        msg = Text("one extra solve per response (stress, ΔTSFC%),\nnot one per design variable",
                   font_size=28, color=ACCENT).next_to(a2, DOWN, buff=0.7)
        self.play(FadeIn(msg))
        self.wait(3.5)
        clear(self)


# ================================================================ 6. Lagrangian / GGP
class S6_GGP(Scene):
    def construct(self):
        chapter_card(self, "Chapter 3", "Lagrangian Topology Optimization", "moving components · GGP")
        # Eulerian vs Lagrangian
        el = Text("Eulerian", font_size=32, color=BLUE_B).shift(LEFT * 3.5 + UP * 2.6)
        la = Text("Lagrangian", font_size=32, color=ACCENT).shift(RIGHT * 3.5 + UP * 2.6)
        grid = VGroup(*[Square(0.35, stroke_width=1, stroke_color=GREY_D,
                               fill_color=BLUE_C, fill_opacity=float(np.random.default_rng(i).uniform() > 0.5))
                        for i in range(100)]).arrange_in_grid(10, 10, buff=0).shift(LEFT * 3.5 + DOWN * 0.2)
        bar = RoundedRectangle(corner_radius=0.25, width=3.2, height=0.5, color=ACCENT,
                               fill_opacity=0.5).rotate(0.4).shift(RIGHT * 3.5 + DOWN * 0.2)
        self.play(Write(el), Write(la))
        self.play(FadeIn(grid), FadeIn(bar))
        t1 = Text("one variable per element\n(millions)", font_size=22).next_to(grid, DOWN)
        t2 = MathTex(r"(x_c,\,y_c,\,L,\,h,\,\theta)", r"\text{ per component}", font_size=30).next_to(bar, DOWN, buff=1.0)
        self.play(FadeIn(t1), FadeIn(t2))
        self.play(bar.animate.shift(UP * 0.5).rotate(-0.8), run_time=1.5)
        self.play(bar.animate.stretch(0.7, 0).shift(DOWN * 0.3), run_time=1)
        self.add(caption("Few, explicit design variables → crisp, CAD-friendly, manufacturable shapes."))
        self.wait(3)
        clear(self)

        # GGP projection
        hdr = Text("Generalized Geometry Projection (GGP)", font_size=34, weight=BOLD).to_edge(UP)
        self.play(Write(hdr))
        n, cs = 16, 0.32
        origin = np.array([-6.6, -2.4, 0])
        cells = VGroup(*[Square(cs, stroke_width=1, stroke_color=GREY_D, fill_opacity=0)
                         .move_to(origin + np.array([(i + 0.5) * cs, (j + 0.5) * cs, 0]))
                         for i in range(n) for j in range(n)])
        th = ValueTracker(0.5)
        cx = ValueTracker(2.6)

        def make_bar():
            return RoundedRectangle(corner_radius=0.0, width=3.4, height=0.8, color=ACCENT,
                                    stroke_width=3, fill_opacity=0).rotate(th.get_value()).move_to(
                origin + np.array([cx.get_value(), 2.56, 0]))

        def fill_cells():
            c = origin + np.array([cx.get_value(), 2.56, 0])
            ct, st = np.cos(th.get_value()), np.sin(th.get_value())
            g = VGroup()
            for k, sq in enumerate(cells):
                d = sq.get_center() - c
                s, t = d[0] * ct + d[1] * st, -d[0] * st + d[1] * ct
                w = 0.5 * (1 + np.tanh((1.7 - abs(s)) / 0.12)) * 0.5 * (1 + np.tanh((0.4 - abs(t)) / 0.12))
                g.add(Square(cs, stroke_width=0, fill_color=BLUE_C, fill_opacity=w).move_to(sq))
            return g

        fills = always_redraw(fill_cells)
        b = always_redraw(make_bar)
        self.play(Create(cells), run_time=1)
        self.add(fills, b)
        steps = VGroup(
            Text("1. choose geometric primitives", font_size=24),
            MathTex(r"2.\;\; W_i(X)\in[0,1]\ \text{smooth characteristic function}", font_size=30),
            MathTex(r"3.\;\; \delta_i^{el}=\frac{\int_{D} W_i\, d\Omega}{\int_{D} d\Omega}\ \text{(local volume fraction)}", font_size=30),
            MathTex(r"4.\;\; E^{el}=\mathbb{M}(\delta^{el}),\quad \rho^{el}=\mathbb{V}(\delta^{el})", font_size=30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        steps.scale_to_fit_width(6.6).move_to(RIGHT * 3.0 + UP * 0.2)
        for s in steps:
            self.play(FadeIn(s, shift=LEFT * 0.2), run_time=0.7)
            self.wait(0.6)
        self.play(th.animate.set_value(-0.6), cx.animate.set_value(2.0), run_time=2.5)
        self.play(th.animate.set_value(0.2), cx.animate.set_value(3.0), run_time=2)
        self.add(caption("A fixed mesh, no re-meshing: the component is projected on the elements."))
        self.wait(2)
        self.remove(*[m for m in self.mobjects if isinstance(m, Text) and m.get_bottom()[1] < -3])
        unif = VGroup(
            Text("Geometry Projection", font_size=26), Text("Moving Morphable Components", font_size=26),
            Text("Moving Node Approach", font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT).move_to(RIGHT * 1.6 + UP * 0.2)
        self.play(FadeOut(steps), FadeIn(unif))
        br = Brace(unif, RIGHT, color=ACCENT)
        bt = Text("special cases\nof GGP", font_size=26, color=ACCENT).next_to(br, RIGHT)
        self.play(GrowFromCenter(br), FadeIn(bt))
        self.wait(3)
        clear(self)

        # live run: official GGP-Python code, thesis settings (Ch.3, Fig. 26e: AMNA, N_GP=4, R=1/2)
        d = np.load(os.path.join(DATA, "ggp_repo_MNA.npz"))
        dens, comps, comp, vol = d["dens"], d["comps"], d["comp"], d["vol"]
        N = len(dens) - 1
        W = 6.4
        cs = W / NELX
        frame = Rectangle(width=W, height=W / 2, color=GREY_B).shift(LEFT * 2.6 + DOWN * 0.6)
        org = frame.get_corner(DL)
        it = ValueTracker(0)

        def img():
            return density_image(dens[int(it.get_value())].T.flatten(), W).move_to(frame)

        def bars():
            g = VGroup()
            for x0, y0, L, h, th_, m in comps[int(it.get_value())]:
                w = float(m) ** 3          # stiffness weight m^gamma_c (gamma_c = 3)
                if w < 0.02:
                    continue
                h = max(h, 0.05)
                g.add(RoundedRectangle(corner_radius=h * cs / 2 * 0.999, width=(L + h) * cs, height=h * cs,
                                       stroke_color=ACCENT, stroke_width=2, stroke_opacity=w,
                                       fill_color=ACCENT, fill_opacity=0.12 * w)
                      .rotate(th_).move_to(org + np.array([x0 * cs, y0 * cs, 0])))
            return g

        im = always_redraw(img)
        bs = always_redraw(bars)
        load = Arrow(frame.get_right() + UP * 0.9, frame.get_right(), color=RED, buff=0)
        wall = VGroup(*[Line(frame.get_corner(UL) + DOWN * k * 0.32,
                             frame.get_corner(UL) + DOWN * k * 0.32 + LEFT * 0.25 + DOWN * 0.2,
                             color=GREY_B) for k in range(11)])
        # clip components to the design domain (like the thesis component plots)
        big = 20
        masks = VGroup(
            Rectangle(width=big, height=big).next_to(frame, LEFT, buff=0),
            Rectangle(width=big, height=big).next_to(frame, RIGHT, buff=0),
            Rectangle(width=big, height=big).next_to(frame, UP, buff=0),
            Rectangle(width=big, height=big).next_to(frame, DOWN, buff=0),
        ).set_style(fill_color=config.background_color, fill_opacity=1, stroke_width=0)
        self.add(im, bs, masks)
        self.play(FadeIn(frame), FadeIn(wall), GrowArrow(load))
        ax = Axes(x_range=[0, N, 50], y_range=[0, 400, 100], x_length=4.2, y_length=3,
                  axis_config={"include_numbers": True, "font_size": 18}).shift(RIGHT * 4.3 + DOWN * 0.6)
        axl = Text("compliance", font_size=20).next_to(ax, UP)
        graph = always_redraw(lambda: ax.plot_line_graph(
            np.arange(int(it.get_value()) + 1), np.minimum(comp[:int(it.get_value()) + 1], 400),
            add_vertex_dots=False, line_color=ACCENT, stroke_width=3))
        counter = always_redraw(lambda: Text(
            f"iteration {int(it.get_value()):3d}   C = {comp[int(it.get_value())]:.4g}   V = {100 * vol[int(it.get_value())]:.1f}%",
            font_size=22).next_to(frame, UP).align_to(frame, LEFT))
        hdr = Text("AMNA · 18 round-ended bars · 108 design variables", font_size=28).to_edge(UP)
        self.play(Create(ax), FadeIn(axl), FadeIn(counter), Write(hdr))
        self.add(graph)
        cap = caption("GGP-Python code, thesis settings (Ch. 3): bars move, rotate, resize and fade out.")
        self.add(cap)
        self.play(it.animate.set_value(N), run_time=14, rate_func=lambda t: t ** 1.3)
        self.remove(cap)
        res = Text(f"C = {comp[-1]:.2f}  (thesis: 84.16)   ·   V = {100 * vol[-1]:.1f}%  (thesis: 40.00%)",
                   font_size=26, color=ACCENT).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(res))
        self.wait(3.5)
        clear(self)


# ================================================================ 7. Application
class S7_Application(Scene):
    def construct(self):
        chapter_card(self, "Application", "Pylon & engine-mount design")
        hdr = Text("Generic engine + design space, multiple flight load cases", font_size=30).to_edge(UP)
        self.play(Write(hdr))
        loads = thesis_image("Ch2/Design_problem_multi_load.png", 2.3).shift(LEFT * 4 + UP * 0.6)
        self.play(FadeIn(loads))
        form = MathTex(r"\min\; V(x)", r"\quad\text{s.t.}\quad",
                       r"\Delta\mathrm{TSFC}\%\le T_0", r",\quad", r"G_{KS}(\sigma)\le 0",
                       font_size=36).shift(RIGHT * 2.0 + UP * 0.9)
        form.scale_to_fit_width(7.2).next_to(loads, RIGHT, buff=0.6)
        form[2].set_color(ACCENT)
        form[4].set_color(RED_B)
        self.play(Write(form))
        nt = Text("fuel-consumption & stress criteria directly inside the loop", font_size=24, color=GREY_B
                  ).scale_to_fit_width(form.width).next_to(form, DOWN, buff=0.3).align_to(form, LEFT)
        self.play(FadeIn(nt))
        self.wait(3)
        self.play(FadeOut(loads), FadeOut(form), FadeOut(nt))

        a = thesis_image("Ch2/MLCS_solution.png", 3.6)
        b = thesis_image("Ch3/pylon_components_300.png", 3.6)
        a_l = Text("Eulerian (SIMP)", font_size=26, color=BLUE_B)
        b_l = Text("Lagrangian (MNA, pylon-box components)", font_size=26, color=ACCENT)
        ga = Group(a, a_l.next_to(a, DOWN)).shift(LEFT * 3.4 + DOWN * 0.1)
        gb = Group(b, b_l.next_to(b, DOWN)).shift(RIGHT * 3.0 + DOWN * 0.1)
        self.play(FadeIn(ga, shift=UP * 0.3))
        self.wait(2)
        self.play(FadeIn(gb, shift=UP * 0.3))
        self.add(caption("Different methods, same load path: variants of one architecture — a design driver for integration."))
        self.wait(5)
        clear(self)


# ================================================================ 8. Conclusion
class S8_Conclusion(Scene):
    def construct(self):
        hdr = Text("Seven challenges, all addressed", font_size=38, weight=BOLD).to_edge(UP)
        self.play(Write(hdr))
        items = [
            "Industrial engine models  →  superelements",
            "Complex design spaces  →  structured 8-node brick meshes",
            "Non-matching meshes  →  Mortar, Internodes, RL-RBF, new WACA",
            "Efficiency & scalability  →  multigrid solvers & filters",
            "Stress constraints  →  Unified Aggregation & Relaxation",
            "Lagrangian approaches  →  Generalized Geometry Projection",
            "Industrial primitives  →  pylon-like box components",
        ]
        rows = VGroup()
        for s in items:
            chk = MathTex(r"\checkmark", color=GREEN)
            rows.add(VGroup(chk, Text(s, font_size=24)).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(hdr, DOWN, buff=0.5)
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.6)
            self.wait(0.6)
        self.wait(2)
        clear(self)

        key = VGroup(
            Text("Take-away", font_size=40, weight=BOLD, color=ACCENT),
            Text("Tip-clearance (fuel consumption) criteria can be put", font_size=30),
            Text("inside topology optimization from the earliest design phase,", font_size=30),
            Text("to explore new engine-to-wing attachments.", font_size=30),
        ).arrange(DOWN, buff=0.3)
        self.play(FadeIn(key[0]))
        self.play(Write(key[1:]), run_time=3)
        self.wait(2)
        pubs = Text("3 journal papers  ·  2 conference articles", font_size=26, color=GREY_B).next_to(key, DOWN, buff=0.7)
        self.play(FadeIn(pubs))
        self.wait(2)
        self.play(FadeOut(key), FadeOut(pubs))

        hdr2 = Text("Perspectives", font_size=38, weight=BOLD).to_edge(UP)
        per = VGroup(
            Text("• unstructured meshes, GPUs, larger design spaces (nacelle, inlet…)", font_size=26),
            Text("• global search: tunneling, surrogate-based EGO", font_size=26),
            Text("• dynamics, non-linear, thermo-mechanical, multi-physics", font_size=26),
            Text("• fatigue-consistent stress allowables", font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        self.play(Write(hdr2))
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.2) for p in per], lag_ratio=0.4), run_time=3)
        self.wait(3)
        clear(self)
        thanks = VGroup(Text("Thank you", font_size=56, weight=BOLD),
                        Text("Simone Coniglio", font_size=30, color=BLUE_B),
                        Text("animated with Manim", font_size=20, color=GREY_B)).arrange(DOWN, buff=0.4)
        self.play(Write(thanks[0]), FadeIn(thanks[1:]))
        self.wait(3)
        self.play(FadeOut(thanks))
