"""Reproduce the thesis' Lagrangian short-cantilever result (Ch. 3, Fig. 26e: AMNA,
N_GP = 4, R = 1/2, 18 round-ended bars, 60x30 mesh, V = 0.4) with the official
GGP-Python code (https://github.com/topggp/GGP-Python), and record the full
optimization history for the Manim animation.

The repository code is used unmodified; we only inject one line that records
(xPhys, component parameters, compliance, volume) at every iteration.

usage: python run_ggp_repo.py /path/to/GGP-Python [settings] [maxiter]
"""
import sys, os, inspect, textwrap, importlib.util
import matplotlib
matplotlib.use("Agg")
import numpy as np

repo = sys.argv[1]
settings = sys.argv[2] if len(sys.argv) > 2 else "MNA"
maxit = int(sys.argv[3]) if len(sys.argv) > 3 else 500

spec = importlib.util.spec_from_file_location("Generalized_projection",
                                              os.path.join(repo, "Generalized_projection.py"))
gp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gp)

src = textwrap.dedent(inspect.getsource(gp.main))
hook = "cvec[iteration-1]=c"
assert src.count(hook) == 1
indent = src.split(hook)[0].split("\n")[-1]
src = src.replace(hook, hook + "\n" + indent + "_REC.append((xPhys.copy(), Xg.copy(), c, v))")
src = src.replace("plot_rate = 1 ", "plot_rate = 10**9 ")   # skip live matplotlib redraws
gp._REC = []
exec(src, gp.__dict__)

it, cvec, vvec, xPhys, xn, yn, Mc, kkt = gp.main(60, 30, 0.4, settings, "Short_Cantiliever", maxit)
rec = gp._REC
dens = np.array([r[0] for r in rec])            # (it, nely, nelx), row 0 = top
comps = np.array([r[1].reshape(-1, 6) for r in rec])  # (it, ncomp, [X, Y, L, h, theta, m])
comp = np.array([r[2] for r in rec]); vol = np.array([r[3] for r in rec])
os.makedirs("data", exist_ok=True)
np.savez(f"data/ggp_repo_{settings}.npz", dens=dens, comps=comps, comp=comp, vol=vol)
print(f"{settings}: {len(rec)} iterations, final compliance {comp[-1]:.2f}, volume {vol[-1]:.3f}")
