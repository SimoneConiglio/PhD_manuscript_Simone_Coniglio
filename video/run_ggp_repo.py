"""Reproduce the thesis' Lagrangian short-cantilever result (Ch. 3, Fig. 25: AGP,
N_GP = 4, R = 1/2, 18 round-ended bars, 60x30 mesh, V = 0.4 -> C = 74.94) with the
GGP framework https://github.com/SimoneConiglio/generalized_geometry_projection
(preset ``short_cantilever``), recording the full history for the Manim animation.

The framework is used unmodified: we only wrap the geometry / physics disciplines'
``_run`` at runtime to store each evaluation.

usage (inside the framework's FEniCS env):
    python run_ggp_repo.py /path/to/generalized_geometry_projection [max_iter]
"""
import sys, os
import numpy as np

repo = os.path.abspath(sys.argv[1])
max_iter = int(sys.argv[2]) if len(sys.argv) > 2 else None
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ggp_repo_GP.npz")
sys.path.insert(0, repo)
os.chdir(repo)

from dataclasses import replace

# The preset documents that the MMA subproblem must be solved with up to 2000 inner
# iterations (the GGP-Matlab reference solves it fully; under-solving breaks the
# symmetry of the solution). gemseo-mma 4.0.0 hard-codes a cap of 200 in subsolv, so we
# raise it at run time (in memory only) to follow the preset's stated settings.
import gemseo_mma.opt.core.mma as _mma
_src = open(_mma.__file__).read()
assert _src.count("ittt < 200") == 1
exec(compile(_src.replace("ittt < 200", "ittt < 2000"), _mma.__file__, "exec"), _mma.__dict__)
from ggp.problem.loader import load_problem  # noqa: E402
import ggp.optimization.pipeline as pl  # noqa: E402

REC = []
_last = {}

_g_run = pl.GGPGeometryDiscipline._run
def g_run(self, input_data=None):
    _g_run(self, input_data)
    x = self.local_data["x_vars"].flatten()
    _last["x"] = self.lb + x * (self.ub - self.lb)
    _last["rho"] = np.asarray(self.local_data["rho_V"]).flatten().copy()
    _last["coords"] = self.eval_coords
pl.GGPGeometryDiscipline._run = g_run

_p_run = pl.GGPPhysicsDiscipline._run
def p_run(self, input_data=None):
    _p_run(self, input_data)
    c = float(np.exp(self.local_data["compliance"][0]) - 1.0)
    v = float(np.mean(_last["rho"]))
    if REC and np.array_equal(REC[-1][0], _last["x"]):
        return  # same design re-evaluated (linearization) -> keep one record per iterate
    REC.append((_last["x"].copy(), _last["rho"].copy(), c, v))
pl.GGPPhysicsDiscipline._run = p_run

spec = load_problem(os.path.join(repo, "ggp", "cli", "presets", "short_cantilever.yaml"))
if max_iter:
    spec = replace(spec, solver=replace(spec.solver, max_iter=max_iter))
res = pl.GGPPipeline(spec).run()

# bin triangle-cell densities onto the 60x30 element grid used by the animation
nelx, nely = 60, 30
xy = _last["coords"]
ix = np.clip((xy[:, 0] / 60.0 * nelx).astype(int), 0, nelx - 1)
iy = np.clip(((30.0 - xy[:, 1]) / 30.0 * nely).astype(int), 0, nely - 1)  # row 0 = top
cnt = np.zeros((nely, nelx)); np.add.at(cnt, (iy, ix), 1)
dens = []
for _, rho, _, _ in REC:
    g = np.zeros((nely, nelx)); np.add.at(g, (iy, ix), rho); dens.append(g / cnt)
os.makedirs(os.path.dirname(out), exist_ok=True)
np.savez(out, dens=np.array(dens), comps=np.array([r[0].reshape(-1, 6) for r in REC]),
         comp=np.array([r[2] for r in REC]), vol=np.array([r[3] for r in REC]))
print(f"iterates {len(REC)}, iterations {res.iterations}, final C {np.exp(res.objective_value) - 1:.3f}, "
      f"recorded C {REC[-1][2]:.3f}, V {REC[-1][3]:.4f}")
