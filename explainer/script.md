# Script: "Designing the pylon around the engine's fuel burn"

Narrated explainer of the thesis *Propulsion Airframe Topology Optimization including
engine performance and stress criteria* (S. Coniglio), built with the
`paper-to-explainer-video` skill. 16 scenes, about 17 minutes.

Every number below has its source in brackets. **Toy** marks a small example computed
in the scene file (not taken from the thesis); the narration says it is an
illustration.

---

## 1. Hook: two pylons
On screen: thesis solutions D and A (App. B, Fig. B.22/B.25) side by side, then their two
points on the Pareto front (V on x, ΔTSFC % on y), drawn from `pareto.mat`.
> Here are two designs for the structure that hangs a jet engine under a wing.
> Both carry the same flight loads, and neither breaks.
> The one on the left uses three point six percent of the available volume. During
> manoeuvres, it lets the engine burn zero point one eight three percent more fuel.
> The one on the right uses about a third more material, four point nine percent, and
> brings that over-consumption down to zero point one six.
> Same engine, same loads. The only difference is where the material sits.
> So where should it go? And how would you even find out? That's what this thesis builds.

[V and ΔTSFC: `images/Ch2/pareto.mat`: Vf = 3.603, Tf = 0.1827; V16 = 4.924, T16 = 0.160]

## 2. Why an engine burns more fuel when it bends
On screen: one engine stage as a ring: the casing (grey), the blades (blue), and the gap
between them. A manoeuvre load bends the casing and shifts the rotor; the gap opens on one
side and closes on the other.
> Inside the engine, rows of blades spin a hair's breadth from a fixed casing.
> That gap is called the tip clearance.
> When the aircraft pulls a manoeuvre, the engine bends. The casing and the rotor move by
> different amounts, so the gap opens here and closes there.
> Where it closes, the blades rub and wear the casing; where it opens, air leaks past the
> blade tips. Either way, the stage works less well, and the engine burns more fuel for
> the same thrust.

## 3. Turning a bent ring into one number (toy)
On screen: the ring with 24 points. At each angle, the casing and rotor displacements are
drawn as arrows, the radial difference δ(θ) is plotted around the ring, then squared,
averaged and square-rooted into a bar, then divided by the blade height.
> To optimize something, we need a number. The thesis builds it in three steps.
> First, at each angle, project the casing and rotor displacements on the radius. Their
> difference is the change in clearance.
> Second, take the root mean square of these changes around the ring. One stage, one
> number.
> Third, divide by the blade height and add the stages up. That's the change in thrust
> specific fuel consumption, delta TSFC, in percent.
> And because the cold clearance must be set so the blades never rub in the worst case,
> it's the worst manoeuvre that matters: with several load cases, we keep the largest.
> Notice that every step is linear or smooth in the displacements. That will matter.

[Definition: Ch. 1 §1.2.2, Eqs. 1.?–1.7: δ = [γ]U, R = sqrt(δᵀδ/N), ΔTSFC % = Σ R_s/l_s·100,
max over load cases. Toy: the ring's displacements are made up for illustration.]

## 4. The design problem
On screen: the generic whole-engine model, the grey design zone between engine and wing,
clamped at the wing, then the three load arrows Fx, Fy, Fz. Counters fill in: elements,
degrees of freedom, Gauss points.
> Here is the playground. A generic engine model: shells for the casings, a beam for the
> shaft, about ten thousand elements.
> Above it, the grey block is everything the aircraft maker controls: the space for the
> pylon and the engine mounts, clamped to the wing.
> It is cut into four hundred eighty-six thousand brick elements: one and a half million
> unknowns, almost four million points where stress must be checked.
> Three loads: thrust along the axis, a lateral load, a vertical load.
> The question: the lightest structure in this block that never exceeds its allowable
> stress, and keeps delta TSFC below a target.

[9,976 engine elements (Fig. 1.?); 486,400 elements, 1,529,847 DOFs, 3,891,200 Gauss
points, 3 load cases (Tables 2.2/2.3)]

## 5. How it's usually done
On screen: three cards, each animating its method on a sketch.
(a) Sizing: a fixed pylon architecture, its panel thicknesses as sliders.
(b) Compliance topology optimization: material carving itself into the stiffest shape.
(c) A search over engine-mount positions.
> The usual approach starts from an architecture someone already drew, and sizes it:
> thicker here, thinner there. Engine and pylon have even been sized together this way.
> But sizing can't invent a new load path.
> Topology optimization can: it decides where material exists at all. It has been used
> on pylons, but to make them stiff, not to protect the engine's clearances.
> And a stiffer pylon is not automatically a better engine neighbour: what matters is
> how the engine deforms, not how much the pylon does.
> Other studies optimized the mount positions with heuristics, on a small region.
> The gap: topology optimization, at industrial scale, with fuel consumption and stress
> inside the loop.

[Bettebghor et al. 2013 (bi-level sizing); Remouchamps et al. 2011 (compliance + drag);
Xue et al. 2012 (ant colony, mounts): Ch. 2 §2.4 intro]

## 6. Idea 1: let every element decide (SIMP)
On screen: random grey densities on the 60×30 cantilever grid; the curve E(x) = x^p with p
going from 1 to 3; then a real SIMP run, density field and compliance counter.
> Give every element a number between zero and one: void or solid. That's the density.
> If grey were allowed for free, the optimizer would happily paint everything grey.
> So stiffness is made to grow like the density cubed: half-dense material gives only an
> eighth of the stiffness for half the weight. Grey stops paying, and the design turns
> black and white.
> Here is a small cantilever, clamped on the left, pushed down on the right. Watch the
> load path appear.

[SIMP law E(x)=Emin+(E−Emin)x^p, p=3 (Eq. 2.6). Run: our top88-style code, 60×30,
V=0.4, density filter r=1.8]

## 7. Two traps, and the filter
On screen: the same run without a filter shows checkerboards; refining the mesh changes the
design. Then the filter as a small averaging disk sliding over the grid, and the clean
result.
> Left alone, this goes wrong in two ways.
> It invents checkerboards: alternating black and white cells that the finite elements
> wrongly see as stiff.
> And refine the mesh, and you get a different, finer design: no answer at all, just
> more detail.
> The cure is a filter: each element's physical density is a weighted average of its
> neighbours within a fixed radius. Checkerboards vanish, and the design stops depending
> on the mesh.
> On a mesh with half a million irregular elements, just finding everyone's neighbours is
> expensive; the thesis builds that filter matrix with a multigrid strategy.

[Numerical instabilities: Ch. 2 §2.2.2 (Sigmund & Petersson 1998); density filter
Eq. 2.16; multigrid filter construction (abstract, §2.2)]

## 8. Fitting the engine in: superelements (toy)
On screen: a chain of three springs. The middle node is condensed: the chain becomes one
equivalent spring, computed live. Then the engine model collapses to the dots on its
interface.
> The engine model comes from the engine maker, in Nastran or Abaqus. We don't want to
> re-implement it, and we can't afford to re-solve it at every iteration.
> Take three springs in a row. If nobody ever pushes on the middle node, we can solve for
> it once and for all. What remains is a single spring between the ends, with exactly the
> same behaviour.
> That's a superelement: K b b minus K b i, K i i inverse, K i b. Exact, not an
> approximation.
> The thesis does this for the whole engine: only the nodes that touch the pylon remain,
> and the tip clearances can still be recovered from them.

[Superelement strategy: abstract, Ch. 1 §1.4; conclusion item 1. Toy: k1=2, k2=3 → 6/5.]

## 9. Gluing meshes that don't match
On screen: the engine interface mesh and the design-zone mesh, nodes not facing each other;
a naive glue lets the interface tear; the tied interface transmits a bending load.
> The engine's mesh and the design block's mesh were made separately. At their interface,
> nodes don't face each other.
> Glue them carelessly and forces leak: the interface no longer transmits the right
> moment.
> The thesis implements and benchmarks four ways of tying them: Mortar, Internodes,
> radial basis functions, and a new one, the weighted average continuity approach,
> together with a correction that restores the balance of moments exactly.

[Ch. 1 §1.3; conclusion item 3; Coniglio et al. 2018 (WACA, moment correction)]

## 10. Stress, and the optimum you can't reach (toy)
On screen: two bars hanging a weight, a short one (weak material) and a long one (strong
material). Both stretch by the same amount, so the short bar's stress doesn't depend on its
thickness. The safe designs in the (x₁, x₂) plane: a big region, plus a spike of zero
thickness along the axis x₁ = 0. The volume contours show the optimum at the spike's tip.
> Now stress. Two bars share a load. They stretch by the same amount, so the short bar
> is always the more stressed one, whatever its thickness.
> Make its material weak, and it can never be safe, unless it isn't there at all.
> Look at the safe designs: a big region, and this spike along the axis, where the short
> bar has vanished. The lightest design is at the tip of the spike: half the volume.
> But the spike has no thickness. Any trace of the short bar, however thin, is unsafe,
> and an optimizer that keeps every density slightly above zero never gets onto it.
> Optima like this are called singular, and topology optimization is full of them.

[Singular optima: Ch. 2 §2.3 (Kirsch 1990, Cheng & Guo 1997). Toy numbers: L₁=1, L₂=2,
σ₁,lim=1, σ₂,lim=4, P=1: volume 1 vs 0.5, computed on screen.]

## 11. Relax and aggregate
On screen: same plane. Each violation is multiplied by the density and the violations are
aggregated with the lower-bound KS function: the spike gets a finite width. Then millions of dots (one per Gauss point) collapse into one KS value; a bar
chart shows the KS value under the true maximum.
> The fix comes in two moves. First, multiply each stress violation by the density of its
> element. A vanishing bar now has a vanishing violation: the danger fades smoothly as
> the bar disappears.
> Second, there are almost four million stress points in the pylon. Instead of four
> million constraints, take a smooth estimate of the largest one, the KS function, built
> to sit slightly below the true maximum.
> That small slack gives the spike a width: a corridor the optimizer can walk down, to
> the lighter design.
> One constraint instead of four million, and singular optima become reachable. The
> thesis calls this unified aggregation and relaxation.

[Relaxed violation ḡ = x(σ̂/σlim − 1) (Eq. 2.30); lower-bound KS (Eq. 2.31/2.32);
UAR: abstract and Ch. 2 §2.3. Toy region computed with P=4.]

## 12. Gradients for the price of one solve
On screen: two counters per iteration. Finite differences: 243,200 extra solves. Adjoint:
one extra solve per response.
> The optimizer needs to know which way to move every one of the two hundred forty-three
> thousand density variables.
> Nudging them one by one would cost one finite-element solve each, per iteration.
> The adjoint method gets all of them from one extra solve per response: one for the
> volume, which is free, one for the stress constraint, one for delta TSFC.
> The thesis derives these adjoints for the fuel-consumption and stress responses.

[243,200 variables (Table 2.3, symmetric); adjoint derivations Ch. 2 §2.4.1.]

## 13. Idea 2: build with parts (GGP)
On screen: left, a pixel grid; right, a round-ended bar with its five parameters. The bar
is projected on the grid: each element gets the fraction of a small sampling window covered
by the bar. Then three method names (MMC, GP, MNA) slide under one brace: GGP.
> Density designs are free, but organic: someone still has to turn them into parts.
> The other family starts from parts: bars, plates, boxes, each described by a few
> numbers, its position, length, thickness and angle. They move and grow; the mesh stays
> fixed.
> To analyse them on that fixed mesh, each element asks: what fraction of a little
> window around me does this bar cover? That fraction becomes its density.
> Three known methods, moving morphable components, geometry projection and the moving
> node approach, look different. The thesis shows they are the same procedure with
> different choices: the generalized geometry projection.

[GGP: Ch. 3 §3.5 (Eqs. for W, δ = window average, M and V maps); Coniglio et al. 2019.]

## 14. Is the projection accurate? (toy)
On screen: one horizontal bar in a 100×50 mesh, clamped left, load on the right. Its
thickness h grows from 1 to 10; the computed compliance is plotted against Euler beam
theory, with 1 and 4 Gauss points per window.
> Before trusting this, check it where we know the answer: one bar, a cantilever,
> classical beam theory.
> For thick bars, the projected model matches the theory. For thin bars, it's too stiff,
> and the curve gets wavy, as the bar's edge crosses the element rows.
> More sample points per window smooth it out. That's the kind of knob the thesis maps,
> for each of the three methods.

[Ch. 3 §3.8.1, Fig. 3.22 (AMMC, R = 0.5, N_GP = 1, 4, 16, 64). Toy: recomputed with our FE
and the GGP projection; we say it is a recomputation.]

## 15. The evidence
On screen: (a) a real run of the GGP framework on the short cantilever: 18 bars moving,
compliance counter, final value vs the thesis. (b) A scorecard of the three methods on that
benchmark. (c) The pylon: SIMP solution vs the MNA solution with pylon boxes and cylinder
mounts, with a table.
> Here's the short cantilever, with eighteen bars, run with the GGP framework and the
> thesis settings: the bars slide, turn and fade into a truss. Compliance seventy-four
> point two; the thesis reports seventy-four point nine.
> On this benchmark, geometry projection did best; moving morphable components and the
> moving node approach both stopped near eighty-four.
> On the pylon, the density method found a well-connected structure using five percent of
> the volume, with delta TSFC at zero point one six.
> With pylon boxes and cylinder mounts, the solution is close to how pylons are actually
> built, but heavier: nine point eight percent of the volume, at a looser target of
> zero point one seven.
> Different methods, different details, but the same load path: variants of one
> architecture.

[2D: Figs. 3.24f/3.25f/3.26f: AMMC 84.50, AGP 74.94, AMNA 84.16 (N_GP=4); our run 74.19.
SIMP multi-load: Table 2.4: V 4.97 %, ΔTSFC 0.1591, σmax 30.08 MPa, T₀ 0.16.
MNA boxes: Table 3.6 results: V 9.79 %, ΔTSFC 0.1698, σmax 30.08 MPa, T₀ 0.17.
Conclusion: "variants of the same architecture".]

## 16. Back to the two pylons
On screen: the Pareto front A–D (from `pareto.mat`); solutions A and D; the front engine
connection highlighted. Then the three-line recap.
> Back to our two pylons. Tightening the target from zero point one eight three to zero
> point one six costs about a third more material, and the four optimized designs show
> where it goes.
> As the target tightens, the front stiffens, in particular the link between the core
> casing and the base of the outlet guide vanes: a key connection for controlling how
> the engine deforms.
> That's the thesis in three lines.
> One: fuel burn can sit inside topology optimization, from the very first sketch.
> Two: at industrial scale, thanks to superelements, mesh tying, filters, relaxation and
> adjoints.
> Three: with densities for freedom, or with parts, unified by the generalized geometry
> projection, for designs closer to what can be built.

[App. B §B.? "TSFC constraint parametric study": A–D with T₀ = 0.16, 0.17, 0.18, 1; the
core casing / OGV connection conclusion.]

---

### Open questions for the author
1. Scene 15: is the T₀ difference between the SIMP (0.16) and MNA-box (0.17) runs worth
   stating as a caveat, or should the comparison show only the SIMP vs MNA-box designs
   without numbers?
2. Scene 9: the thesis benchmark compares accuracy and CPU time of the tying methods. I
   kept it qualitative. Do you want specific numbers from Ch. 1 §1.3.4?
3. Scene 3: the ring displacements are made up for illustration. Should I use real values
   from the engine model if you have them?
4. Voice: Kokoro `am_michael` (US English) by default. Another voice or accent?
