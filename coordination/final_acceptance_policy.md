# Final datasets and numerical acceptance

The supplied enhanced mesh establishes the common physical aerofoil position. Its shared leading-edge endpoint and the trailing-edge midpoint give a rigid translation of the original constructed profile by (0.00048367698354395, 0.00691690311771526) m, without moving the duct. See the independently reproducible NACA fit in `review/enhanced_naca_profile_fit_audit.json`.

Formal Cases 1–3 must use the independently generated `aligned_taskA` mesh and `_aligned` solver datasets. Earlier baseline cases remain historical prealignment records. They are excluded from the final five-case comparison. The baseline sizing remains the required 10/2 mm with growth 1.05.

The initial enhanced RSM diagnostic remains separate from the five comparison cases. Its actual first residual crossing occurred at 432 iterations and must not be rewritten as a failed attempt.

Case 4 first crossed the default 1e-3 residual threshold at iteration 215, but its drag still changed materially. Preserve that state and its original Case 5 continuation. Final Cases 4 and 5 use the separately stored `_verified` extensions, with Case 5 continuing the accepted Case 4 data rather than being hybrid-initialised.

Two events must be recorded separately:

1. First satisfaction of the default 1e-3 residual condition, corresponding to the coursework iteration count.
2. The final stopping iteration and state used for reported forces and field data.

The additional numerical-verification targets were selected by the analysis team, not supplied as coursework requirements: all active scaled residuals at or below 1e-5, plus both lift and drag ranges divided by the absolute window mean at or below 0.1% across 100 consecutive new-model iterations. Seed rows, repeated report rows and inherited iterations do not count as new model updates. These targets help separate iterative error from model, mesh and input differences; they are not physical validation criteria.

If a model does not meet these targets within a documented iteration cap or exhibits persistent oscillation, preserve its actual residuals, force windows and termination reason. Do not label it fully converged or assign false precision. A marker from an earlier residual stage does not establish success at a later tighter stage.

Case 5 records global iteration, inherited seed iteration and new RSM update count separately. Final comparison tables must identify whether an iteration entry is the first threshold crossing or the final stopping count; Case 5 counts are incremental RSM updates, with its seed identified.

Supplementary SA grid checks use the aligned geometry at all three resolutions with unchanged physical and numerical settings. The independent k-epsilon length-scale sensitivity compares the final aligned baseline at L=1 m against an otherwise identical L=0.01 m run. The latter is an analyst-chosen sensitivity value, not a measured experimental input. Neither study overwrites or silently replaces a required formal case.
