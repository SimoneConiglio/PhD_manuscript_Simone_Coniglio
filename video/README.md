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
| S6 GGP (Ch. 3) | Eulerian vs Lagrangian, GGP projection, **thesis AGP run** |
| S7 Application | pylon / engine-mount results (figures from the manuscript) |
| S8 Conclusion | the 7 challenges, take-away, perspectives |

## Data behind the optimization animations
* `topopt_data.py`: top88-style SIMP with a density filter → `data/simp.npz`.
* `run_ggp_repo.py`: runs the
  [generalized_geometry_projection](https://github.com/SimoneConiglio/generalized_geometry_projection)
  framework **unmodified** (its disciplines are only wrapped at run time to record each
  iterate) with its `short_cantilever` preset, i.e. the thesis settings of Ch. 3
  (60×30, V = 0.4, AGP, 18 bars, N_GP = 4, R = 1/2, MMA) → `data/ggp_repo_GP.npz`.
  Thesis reference (Fig. 25f): C = 74.94, V = 40.00 % at iteration 122.

## Rendering
```bash
pip install manim matplotlib            # needs LaTeX, ffmpeg, pango (see Manim docs)
# only needed to recompute data/ggp_repo_GP.npz (FEniCS env from the framework's environment.yml):
git clone https://github.com/SimoneConiglio/generalized_geometry_projection /path/to/ggp
GGP_REPO=/path/to/ggp GGP_PYTHON="micromamba run -n ggp python" ./render.sh h   # l = 480p preview
```
Output: `video/thesis_explainer.mp4`.  The video has on-screen captions and no voice-over.
