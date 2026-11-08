# Thesis explainer video (Manim)

A ~6-minute animated explainer of the thesis *Propulsion Airframe Topology Optimization
including engine performance and stress criteria*, made with
[Manim Community](https://www.manim.community/), the community edition of the library
3Blue1Brown uses for its videos.

| Scene | Content |
|---|---|
| S1 Intro | CO₂ context, UHBR engines |
| S2 Tip clearance | casing ovalisation under manoeuvre loads, ΔTSFC, design space, roadmap |
| S3 FEM (Ch. 1) | KU = F, superelements, non-matching mesh tying (WACA), multigrid solvers |
| S4 SIMP (Ch. 2) | density field, penalisation, filter, **real SIMP run** (60×30, V = 0.4) |
| S5 Stress (Ch. 2) | von Mises, singular optima, Unified Aggregation & Relaxation, adjoint |
| S6 GGP (Ch. 3) | Eulerian vs Lagrangian, GGP projection, **thesis AMNA run** |
| S7 Application | pylon / engine-mount results (figures from the manuscript) |
| S8 Conclusion | the 7 challenges, take-away, perspectives |

## Data behind the optimization animations
* `topopt_data.py`: top88-style SIMP with a density filter → `data/simp.npz`.
* `run_ggp_repo.py`: runs the official [GGP-Python](https://github.com/topggp/GGP-Python)
  code **unmodified** (one recording line is injected at run time) with the thesis
  settings of Ch. 3 (short cantilever, 60×30, V = 0.4, AMNA, 18 bars, N_GP = 4, R = 1/2)
  → `data/ggp_repo_MNA.npz`. Result: C = 84.00, V = 40.0 % after 145 iterations, vs.
  C = 84.16, V = 40.00 % at iteration 150 in the thesis (Fig. 26e/f).

## Rendering
```bash
pip install manim matplotlib            # needs LaTeX, ffmpeg, pango (see Manim docs)
git clone https://github.com/topggp/GGP-Python /path/to/GGP-Python
GGP_REPO=/path/to/GGP-Python ./render.sh h     # l = 480p preview, h = 1080p60
```
Output: `video/thesis_explainer.mp4`.  The video has on-screen captions and no voice-over.
