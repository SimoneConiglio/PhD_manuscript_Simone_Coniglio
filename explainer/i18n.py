"""Language switch for video.py: VIDEO_LANG=fr-fr renders the French version.

Narration is translated from narration_fr.json (keyed by the English sentence); on-screen
text through TEXT (exact strings), REGEX (formatted strings) and French decimal commas.
Every English string must have a translation: a missing one raises, so nothing is left
in English by accident.
"""
import json
import os
import re
from pathlib import Path

FR = os.environ.get("VIDEO_LANG", "en-us").lower().startswith("fr")
_NARR = json.loads((Path(__file__).with_name("narration_fr.json")).read_text()) if FR else {}

TEXT = {
    "(this stage, blade height 50 mm)": "(cet étage, hauteur d'aube 50 mm)",
    "+ a correction restoring the balance of moments": "+ une correction qui rétablit l'équilibre des moments",
    "0 = void": "0 = vide", "1 = solid": "1 = plein",
    "1 point per window": "1 point par fenêtre", "4 points per window": "4 points par fenêtre",
    "1.  Fuel burn can sit inside topology optimization, from the first sketch.":
        "1.  La consommation peut entrer dans l'optimisation topologique, dès la première esquisse.",
    "2.  At industrial scale: superelements, mesh tying, filters, relaxation, adjoints.":
        "2.  À l'échelle industrielle : superéléments, raccord de maillages, filtres, relaxation, adjoints.",
    "3.  With densities for freedom, or with parts unified by GGP, closer to what can be built.":
        "3.  Avec des densités pour la liberté, ou des pièces unifiées par la GGP, plus proches du fabricable.",
    "1. clearance change at each angle": "1. variation de jeu à chaque angle",
    "2. root mean square: one number per stage": "2. moyenne quadratique : un nombre par étage",
    "120 × 60, filtered": "120 × 60, filtré", "120 × 60, no filter": "120 × 60, sans filtre",
    "60 × 30, filtered": "60 × 30, filtré", "60 × 30, no filter": "60 × 30, sans filtre",
    "Euler beam theory": "théorie des poutres d'Euler",
    "Geometry Projection": "Projection géométrique", "Internodes": "Internodes", "Mortar": "Mortar",
    "Moving Morphable Components": "Composants mobiles déformables", "Moving Node Approach": "Approche des nœuds mobiles",
    "Moving Morphable\nComponents": "Composants mobiles\ndéformables", "Geometry\nProjection": "Projection\ngéométrique",
    "Moving Node\nApproach": "Approche des\nnœuds mobiles",
    "New: weighted average continuity approach": "Nouveau : continuité par moyenne pondérée",
    "Radial basis functions (RL-RBF)": "Fonctions à base radiale (RL-RBF)",
    "Propulsion Airframe Topology Optimization": "Propulsion Airframe Topology Optimization",
    "including engine performance and stress criteria": "including engine performance and stress criteria",
    "Simone Coniglio · PhD thesis, Université de Toulouse": "Simone Coniglio · Thèse de doctorat, Université de Toulouse",
    "The gap: topology optimization, industrial scale, fuel burn and stress in the loop":
        "Le manque : optimisation topologique, échelle industrielle, consommation et contrainte dans la boucle",
    "The thesis in three lines": "La thèse en trois lignes",
    "Where should it go?  And how would you find out?": "Où la mettre ?  Et comment le savoir ?",
    "a finer mesh gives a different design": "un maillage plus fin donne une autre conception",
    "a singular optimum": "un optimum singulier",
    "adjoint: extra solves per iteration": "adjoint : calculs en plus par itération",
    "can't invent a new load path": "n'invente pas de chemin d'effort",
    "checkerboards": "damiers", "clamped to the wing": "encastré sur l'aile",
    "closes: blades rub": "se ferme : les aubes frottent", "opens: air leaks": "s'ouvre : l'air fuit",
    "compliance (lower is better)": "compliance (plus bas = mieux)", "compliance": "compliance",
    "core casing  ↔  outlet guide vane base": "carter primaire  ↔  base des aubes directrices",
    "delta TSFC 0.159 %   (target 0.16)": "delta TSFC 0,159 %   (cible 0,16)",
    "delta TSFC 0.170 %   (target 0.17)": "delta TSFC 0,170 %   (cible 0,17)",
    "densities (SIMP)": "densités (SIMP)", "densities: free, but organic": "densités : libres, mais organiques",
    "density": "densité", "stiffness": "raideur",
    "derived in the thesis for the stress and fuel-consumption responses":
        "établis dans la thèse pour les réponses de contrainte et de consommation",
    "design variables": "variables de conception", "design zone: pylon + mounts": "zone de conception : mât + attaches",
    "engine model": "modèle moteur", "every step: linear or smooth in the displacements":
        "chaque étape : linéaire ou lisse en fonction des déplacements",
    "exact, not an approximation": "exact, pas une approximation",
    "extra fuel (%)": "surconsommation (%)", "extra fuel in manoeuvres (%)": "surconsommation en manœuvre (%)",
    "from the engine maker: Nastran / Abaqus": "fourni par le motoriste : Nastran / Abaqus",
    "half a million irregular elements: the filter matrix is built with a multigrid strategy":
        "un demi-million d'éléments irréguliers : matrice de filtre construite par multigrille",
    "long, strong": "longue, solide", "short, weak": "courte, faible", "manoeuvre load": "charge de manœuvre",
    "max stress 30.1 MPa": "contrainte max 30,1 MPa", "moment not transmitted": "moment non transmis",
    "more fuel for the same thrust": "plus de carburant pour la même poussée",
    "the stage works less well": "l'étage fonctionne moins bien",
    "nudge one by one: extra solves per iteration": "une par une : calculs en plus par itération",
    "parts: pylon boxes + cylinder mounts (MNA)": "pièces : caissons de mât + attaches cylindriques (MNA)",
    "reachable, not guaranteed": "atteignable, pas garanti",
    "recomputed with the GGP-Python projection (AMMC), thesis Fig. 3.22 settings":
        "recalculé avec la projection de GGP-Python (AMMC), réglages de la fig. 3.22 de la thèse",
    "same load path: variants of one architecture": "même chemin d'effort : variantes d'une même architecture",
    "same loads, no failure": "mêmes charges, aucune rupture",
    "special cases of\nGGP": "cas particuliers\nde la GGP",
    "stiff pylon  ≠  engine-friendly": "mât raide  ≠  bon pour le moteur",
    "stiffened as the target tightens": "rigidifiée quand la cible se resserre",
    "targets differ: the volumes are not a like-for-like comparison": "cibles différentes : volumes pas directement comparables",
    "thesis results, 4 sample points per window": "résultats de la thèse, 4 points par fenêtre",
    "tied: forces and moments balanced": "raccordé : efforts et moments équilibrés",
    "tip clearance": "jeu en bout d'aube", "toy displacements, for illustration": "déplacements fictifs, pour illustrer",
    "unified aggregation and relaxation": "agrégation et relaxation unifiées",
    "volume (%)": "volume (%)", "volume of material (%)": "volume de matière (%)",
    "brick elements": "éléments briques", "unknowns": "inconnues", "stress points": "points de contrainte",
    "Sizing": "Dimensionnement", "Compliance topology": "Topologie en compliance", "Mount search": "Recherche d'attaches",
    "Turning a bent ring into one number": "D'un anneau déformé à un seul nombre",
    "The playground": "Le terrain de jeu", "How it's usually done": "Comment on fait d'habitude",
    "Idea 1: let every element decide": "Idée 1 : chaque élément décide",
    "Two traps, and the filter": "Deux pièges, et le filtre",
    "Fitting the engine in: superelements": "Intégrer le moteur : les superéléments",
    "Gluing meshes that don't match": "Raccorder des maillages incompatibles",
    "Stress, and the optimum you can't reach": "La contrainte, et l'optimum inaccessible",
    "Relax and aggregate": "Relaxer et agréger",
    "Gradients for the price of one solve": "Des gradients pour le prix d'un calcul",
    "Idea 2: build with parts": "Idée 2 : construire avec des pièces",
    "Is the projection accurate?": "La projection est-elle précise ?",
    "The evidence: a real run": "La preuve : un vrai calcul",
    "Same benchmark, three methods": "Même cas test, trois méthodes",
    "The pylon": "Le mât", "Back to the two pylons": "Retour aux deux mâts",
}
REGEX = [
    (r"^another start \(orange\): volume (.*)$", r"autre départ (orange) : volume \1"),
    (r"^compliance (\S+)    thesis: (\S+)$", r"compliance \1    thèse : \2"),
    (r"^extra fuel (\S+) %$", r"surconsommation \1 %"),
    (r"^iteration(\s+\d+)(\s+)compliance (.*)$", r"itération\1\2compliance \3"),
    (r"^same start: volume (\S+) \(red\)  vs  (\S+) \(green\)$", r"même départ : volume \1 (rouge)  contre  \2 (vert)"),
    (r"^volume ([\d.]+)( %)?$", r"volume \1\2"),
    (r"^[\d.,]+$", None),
    (r"^[A-Z][a-z]+ et al\. \d{4}$", None),          # references stay as they are
    (r"^[A-D]$", None),
]
TEX = {r"\text{volume}": r"\text{volume}", r"\text{s.t.}": r"\text{t.q.}",
       r"\text{does not depend on } x_1": r"\text{ne d\'epend pas de } x_1", r"\text{per response}": r"\text{par r\'eponse}"}


def _decimal(s):
    return re.sub(r"(\d)\.(\d)", r"\1,\2", s)


def tr(s):
    """On-screen text in the current language."""
    if not FR:
        return s
    if s in TEXT:
        return TEXT[s]
    for pat, rep in REGEX:
        if re.match(pat, s):
            return _decimal(s if rep is None else re.sub(pat, rep, s))
    raise KeyError(f"no French text for {s!r}")


def tr_tex(s):
    if not FR:
        return s
    for a, b in TEX.items():
        s = s.replace(a, b)
    s = re.sub(r"(\d)\.(\d)", r"\1{,}\2", s)
    return s


def narr(s):
    if not FR:
        return s
    if s not in _NARR:
        raise KeyError(f"no French narration for {s[:60]!r}")
    return _NARR[s]


def fmt_int(v):
    s = f"{int(round(v)):,}"
    return s.replace(",", " ") if FR else s
