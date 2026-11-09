"""Pre-compute the data the scenes replay (everything else is computed in video.py).

    python precompute.py /path/to/GGP-Python

* data/simp_nofilter_60.npz, data/simp_nofilter_120.npz, data/simp_filter_120.npz:
  top88-style SIMP on the short cantilever (V = 0.4, p = 3) without / with a density
  filter of fixed physical radius, to show checkerboards and mesh dependence (Ch. 2 §2.2.2).
* data/bar_hc.npz: compliance of one round-ended bar (AMMC projection of the GGP-Python
  code, thesis Fig. 3.22 settings: eps = 0.7, beta = 1e-3, q = 3, R = 0.5) on a 100x50
  cantilever mesh vs its thickness h, for N_GP = 1 and 4, and Euler beam theory.
Already in data/: simp.npz (60x30 filtered run) and ggp_repo_GP.npz (GGP framework run).
"""
import os, sys, importlib.util
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

NU = 0.3


def lk():
    k = np.array([1/2-NU/6, 1/8+NU/8, -1/4-NU/12, -1/8+3*NU/8, -1/4+NU/12, -1/8-NU/8, NU/6, 1/8-3*NU/8])
    return 1/(1-NU**2)*np.array([
        [k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7]], [k[1], k[0], k[7], k[6], k[5], k[4], k[3], k[2]],
        [k[2], k[7], k[0], k[5], k[6], k[3], k[4], k[1]], [k[3], k[6], k[5], k[0], k[7], k[2], k[1], k[4]],
        [k[4], k[5], k[6], k[7], k[0], k[1], k[2], k[3]], [k[5], k[4], k[3], k[2], k[1], k[0], k[7], k[6]],
        [k[6], k[3], k[4], k[1], k[2], k[7], k[0], k[5]], [k[7], k[2], k[1], k[4], k[3], k[6], k[5], k[0]]])


KE = lk()


class Cantilever:
    """Q4 plane-stress cantilever: left edge clamped, unit downward load at mid right."""

    def __init__(self, nelx, nely):
        self.nelx, self.nely = nelx, nely
        self.ndof = 2*(nelx+1)*(nely+1)
        e = np.zeros((nelx*nely, 8), dtype=int)
        for elx in range(nelx):
            for ely in range(nely):
                n1, n2 = (nely+1)*elx+ely, (nely+1)*(elx+1)+ely
                e[ely+elx*nely] = [2*n1+2, 2*n1+3, 2*n2+2, 2*n2+3, 2*n2, 2*n2+1, 2*n1, 2*n1+1]
        self.edof = e
        self.iK = np.kron(e, np.ones((8, 1))).flatten()
        self.jK = np.kron(e, np.ones((1, 8))).flatten()
        self.free = np.setdiff1d(np.arange(self.ndof), np.arange(2*(nely+1)))
        self.F = np.zeros(self.ndof)
        self.F[2*((nely+1)*nelx + nely//2)+1] = -1.0
        self.xc = np.repeat(np.arange(nelx)+0.5, nely)
        self.yc = np.tile(nely-(np.arange(nely)+0.5), nelx)

    def solve(self, E):
        sK = (KE.flatten()[None].T*E).flatten(order='F')
        K = coo_matrix((sK, (self.iK, self.jK)), shape=(self.ndof,)*2).tocsc()[self.free][:, self.free]
        u = np.zeros(self.ndof); u[self.free] = spsolve(K, self.F[self.free])
        ce = (u[self.edof] @ KE * u[self.edof]).sum(1)
        return float(self.F @ u), ce


def simp(nelx, nely, rmin=None, maxit=80, vf=0.4, p=3.0):
    m = Cantilever(nelx, nely); n = nelx*nely
    if rmin:
        r, c, v = [], [], []
        for i in range(n):
            d = np.hypot(m.xc-m.xc[i], m.yc-m.yc[i]); j = np.where(d < rmin)[0]
            r += [i]*len(j); c += list(j); v += list(rmin-d[j])
        H = coo_matrix((v, (r, c)), shape=(n, n)).tocsc(); Hs = np.asarray(H.sum(1)).ravel()
    x = vf*np.ones(n); xp = x.copy(); hist, comp = [xp.copy()], []
    for _ in range(maxit):
        E = 1e-9 + xp**p*(1-1e-9)
        c, ce = m.solve(E); comp.append(c)
        dc = -p*xp**(p-1)*ce; dv = np.ones(n)
        if rmin:
            dc = H @ (dc/Hs); dv = H @ (dv/Hs)
        l1, l2 = 0, 1e9
        while (l2-l1)/(l1+l2) > 1e-3:
            lm = 0.5*(l1+l2)
            xn = np.clip(x*np.sqrt(np.maximum(-dc/dv/lm, 0)), np.maximum(0, x-0.2), np.minimum(1, x+0.2))
            xq = (H @ xn)/Hs if rmin else xn
            l1, l2 = (lm, l2) if xq.sum() > vf*n else (l1, lm)
        x, xp = xn, xq; hist.append(xp.copy())
    comp.append(m.solve(1e-9 + xp**p*(1-1e-9))[0])
    return np.array(hist), np.array(comp)


def bar_curve(gp, nelx=100, nely=50, hs=np.arange(1.0, 10.01, 0.25)):
    m = Cantilever(nelx, nely)
    p = dict(method='MMC', alp=1, epsi=0.7, bet=1e-3, aggregation='KSl', ka=10, saturation=False, zp=1)
    q, R = 3, 0.5
    out = {}
    for ngp in (1, 2):
        if ngp == 1:
            off, w = np.zeros((1, 2)), np.ones(1)
        else:
            g, wg = gp.lgwt(ngp, -R, R)
            gx, gy = np.meshgrid(g, g); off = np.column_stack([gx.ravel(), gy.ravel()])
            w = np.outer(wg, wg).ravel()
        cs = []
        for h in hs:
            # the code aggregates >= 2 components: the same bar twice is the same geometry
            Xg = np.tile([50.0, 25.0, 100.0, h, 0.0, 1.0], 2)
            Wk = np.stack([np.ravel(gp.Wgp(m.xc+o[0], m.yc+o[1], Xg, p)[0]) for o in off])  # (ngp^2, nel)
            delta_c = (w[:, None]*Wk**q).sum(0)/w.sum()
            cs.append(m.solve(delta_c)[0])          # AMMC: E = E0 * delta_c
        out[ngp*ngp] = np.array(cs)
    euler = 4*100.0**3/hs**3                          # C = P delta = 4 P^2 L^3 / (E b h^3)
    np.savez("data/bar_hc.npz", h=hs, c1=out[1], c4=out[4], euler=euler)
    print("bar: h=1", out[1][0], out[4][0], euler[0], " h=10", out[1][-1], out[4][-1], euler[-1])


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    spec = importlib.util.spec_from_file_location("gp", os.path.join(sys.argv[1], "Generalized_projection.py"))
    gp = importlib.util.module_from_spec(spec); spec.loader.exec_module(gp)
    bar_curve(gp)
    for name, args in (("simp_nofilter_60", (60, 30, None)), ("simp_nofilter_120", (120, 60, None)),
                       ("simp_filter_120", (120, 60, 3.6))):
        h, c = simp(*args)
        np.savez(f"data/{name}.npz", hist=h, comp=c, nelx=args[0], nely=args[1])
        print(name, "C =", c[-1])
