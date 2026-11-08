"""Pre-compute the SIMP (Eulerian) optimization history used by the Manim scenes:
short cantilever, 60x30 mesh, V = 0.4, p = 3, density filter (top88-style).
Saved to data/simp.npz.  The Lagrangian (GGP) history comes from run_ggp_repo.py.
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
import os

os.makedirs("data", exist_ok=True)
NELX, NELY, VOLFRAC, PENAL, RMIN = 60, 30, 0.4, 3.0, 1.8
E0, EMIN, NU = 1.0, 1e-9, 0.3


def lk():
    k = np.array([1/2-NU/6, 1/8+NU/8, -1/4-NU/12, -1/8+3*NU/8,
                  -1/4+NU/12, -1/8-NU/8, NU/6, 1/8-3*NU/8])
    return E0/(1-NU**2)*np.array([
        [k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7]],
        [k[1], k[0], k[7], k[6], k[5], k[4], k[3], k[2]],
        [k[2], k[7], k[0], k[5], k[6], k[3], k[4], k[1]],
        [k[3], k[6], k[5], k[0], k[7], k[2], k[1], k[4]],
        [k[4], k[5], k[6], k[7], k[0], k[1], k[2], k[3]],
        [k[5], k[4], k[3], k[2], k[1], k[0], k[7], k[6]],
        [k[6], k[3], k[4], k[1], k[2], k[7], k[0], k[5]],
        [k[7], k[2], k[1], k[4], k[3], k[6], k[5], k[0]]])


KE = lk()
ndof = 2*(NELX+1)*(NELY+1)
edofMat = np.zeros((NELX*NELY, 8), dtype=int)
for elx in range(NELX):
    for ely in range(NELY):
        el = ely+elx*NELY
        n1 = (NELY+1)*elx+ely
        n2 = (NELY+1)*(elx+1)+ely
        edofMat[el] = [2*n1+2, 2*n1+3, 2*n2+2, 2*n2+3, 2*n2, 2*n2+1, 2*n1, 2*n1+1]
iK = np.kron(edofMat, np.ones((8, 1))).flatten()
jK = np.kron(edofMat, np.ones((1, 8))).flatten()
# short cantilever: left edge clamped, downward load at mid right edge
fixed = np.arange(0, 2*(NELY+1))
free = np.setdiff1d(np.arange(ndof), fixed)
F = np.zeros(ndof)
F[2*(NELX+1)*(NELY+1)-NELY-1] = -1.0  # y-dof of mid node on right edge

# element centroids (x right, y up)
xc = np.repeat(np.arange(NELX)+0.5, NELY)
yc = np.tile(NELY-(np.arange(NELY)+0.5), NELX)


def fe(xphys):
    sK = ((KE.flatten()[np.newaxis]).T*(EMIN+xphys**PENAL*(E0-EMIN))).flatten(order='F')
    K = coo_matrix((sK, (iK, jK)), shape=(ndof, ndof)).tocsc()
    K = K[free, :][:, free]
    u = np.zeros(ndof)
    u[free] = spsolve(K, F[free])
    ce = (u[edofMat] @ KE * u[edofMat]).sum(1)
    c = ((EMIN+xphys**PENAL*(E0-EMIN))*ce).sum()
    dc = -PENAL*xphys**(PENAL-1)*(E0-EMIN)*ce
    return c, dc, u


def simp(maxit=80):
    # density filter matrix
    rows, cols, vals = [], [], []
    for i in range(NELX*NELY):
        d = np.hypot(xc-xc[i], yc-yc[i])
        j = np.where(d < RMIN)[0]
        rows += [i]*len(j); cols += list(j); vals += list(RMIN-d[j])
    H = coo_matrix((vals, (rows, cols)), shape=(NELX*NELY,)*2).tocsc()
    Hs = np.asarray(H.sum(1)).ravel()
    x = VOLFRAC*np.ones(NELX*NELY)
    xphys = x.copy()
    hist, comp = [xphys.copy()], []
    for it in range(maxit):
        c, dc, _ = fe(xphys)
        comp.append(c)
        dv = np.ones_like(x)
        dc = H @ (dc/Hs); dv = H @ (dv/Hs)
        l1, l2, move = 0, 1e9, 0.2
        while (l2-l1)/(l1+l2) > 1e-3:
            lm = 0.5*(l2+l1)
            xn = np.clip(x*np.sqrt(np.maximum(-dc/dv/lm, 0)), np.maximum(0, x-move), np.minimum(1, x+move))
            xp = (H @ xn)/Hs
            if xp.sum() > VOLFRAC*x.size: l1 = lm
            else: l2 = lm
        x, xphys = xn, xp
        hist.append(xphys.copy())
    c, _, u = fe(xphys); comp.append(c)
    np.savez("data/simp.npz", hist=np.array(hist), comp=np.array(comp), nelx=NELX, nely=NELY, u=u)
    print("SIMP final compliance", comp[-1])


if __name__ == "__main__":
    simp()
