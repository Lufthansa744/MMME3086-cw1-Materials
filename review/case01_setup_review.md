# Independent Case 1 setup review

**Historical prealignment run:** the main agent has now required a translated baseline matching the supplied enhanced foil placement and independent Case 1–3 reruns under `_aligned` identifiers. This review and its numerical results remain valid for the retained original run but must not populate the final prescribed five-case comparison. Final aligned evidence needs its own review.

Sources inspected read-only: `solver/case01/settings/case01_setup.set`, `case01_setup.cas.h5` (existence only), and actual `solver/case01/logs/setup.transcript`. The reviewer did not use the Fluent session. Conclusions refer to this pre-iteration setup snapshot; the final saved case/settings must also be retained if monitors or numerical controls are subsequently changed.

## Verified setup

| Item | Actual evidence | Assessment |
| --- | --- | --- |
| Release | Settings case version 222 and actual executable/build in transcript | Fluent 2022 R2 |
| Model | `case-config` rp-sa=1, rp-turb=true, rp-ke/rsm=false; TUI selects `spalart-allmaras yes` | S–A selected |
| Solver and dimensions | rp-seg=true, rp-unsteady=false, rp-axi=false, rp-3d=false, rp-double=true; parallel function `2ddp` | Steady pressure-based planar 2D double precision |
| Coupling | TUI `/solve/set/p-v-coupling 20` accepted without error | SIMPLE selected; still request final current-value readback |
| Fluid | Actual material listing and saved air material constant density 1.225 and constant viscosity 1.7894e-5 | kg/m³ and Pa s respectively |
| Inlet | Saved velocity-spec=2 and actual TUI says magnitude normal to boundary, absolute frame, 50.9 m/s; actual mesh inlet x=-0.5 m | Normal inflow is along +x; nominal magnitude correct |
| Inlet turbulence | Actual TUI selects intensity and length scale and retains displayed 5 percent/1 m; saved ke-spec=1, intensity=0.05, length-scale=1 | Actual specified values, not inferred from viscosity ratio |
| Outlet | Actual TUI retains gauge pressure 0 Pa; saved p constant=0, pressure-outlet type | Correct retained default pressure outlet |
| Outlet backflow | Actual TUI retains turbulent viscosity ratio 10; saved ke-spec=2 and viscosity-ratio=10 | This is an outlet backflow input, distinct from inlet intensity specification |
| Force reference | Saved reference velocity 50.9 m/s, length 0.1 m and area 0.1 m²; transcript actual depth=1 command accepted | Chord/area/speed match task planform convention; depth command retained, final scalar readback requested |
| Residual thresholds | Actual convergence-criteria prompts and saved settings give 0.001 for continuity, x-velocity, y-velocity, nut | Four configured criteria, not a claim of convergence |
| Saved artifacts | Initial relative-path writes failed; subsequent absolute-path write-settings and write-case complete successfully with matching mesh counts | Failed attempts retained in log; real successful snapshot identified |
| Force monitor definitions created afterward | Actual TUI includes all three foil zones, drag vector (1,0), lift (0,1), scaled=no, frequency=1 | Correct intended dimensional total-force reporting directions/zone coverage; snapshot predates these additions, so final case/settings require a later save |

The saved file contains inactive fields as well as selected inputs. Inlet `u=0,v=0` does not mean a zero inlet because its selected specification is normal magnitude 50.9. Likewise the saved viscosity-ratio=10 and nut=0.0001 fields are not the chosen inlet turbulence specification when intensity/length is active. Do not mix those fields into the report as simultaneous independently prescribed conditions.

## Derived B0/reference values from these actual inputs

With rho=1.225, mu=1.7894e-5, U=50.9, c=0.1, I=0.05 and S=0.1 in SI units:

- Chord Reynolds number: 348454.7893, suitably reported approximately 3.485e5
- Isotropic one-component RMS fluctuation: I U = 2.545 m/s
- Dynamic pressure: 1586.871125 Pa
- Force normalization q S: 158.6871125 N
- Derived isotropic k relation: 9.7155375 m²/s²; this is a relation from the specified intensity, not a claim that the S–A model solves a k equation

The inlet length scale actually retained is 1 m, ten chords and about 6.67 duct heights. Record it honestly as an inlet turbulence assumption; do not substitute a more plausible-looking smaller number without an explicit, separately saved setup change. Its physical influence should be considered when interpreting fully turbulent model comparisons.

## Not yet established by the inspected sources

Actual final momentum, pressure and modified-viscosity discretization schemes; gradient scheme; current pressure/momentum/nut and other under-relaxation factors; operating pressure; an explicit current reference-depth readback; and the actual initialization command/status are not yet reported. The `context/map-r17+` block contains conditional solution-strategy rules for many methods and must not be read as the current values. `hyb-init?=true` in case configuration is not proof that hybrid initialization was executed or completed. Solver has been asked to log current scalar/control values and actual initialization without this reviewer accessing its session.

No result convergence, residual decline, force stability, y-plus suitability or mass balance has been approved before iteration results are available.

## FAQ source now inspected directly

The actual saved `inputs/FAQ_2026-11-07.png` was visually read. Q7 confirms fixed x=0.05,0.10,0.20 m stations. Q24 explicitly calls the S–A wall-function-selector wording an assignment oversight. Q23 permits intensity/length specification or using actual k–epsilon intensity for the B0 fluctuation calculation; Q17 requests fluctuation rather than calculating intensity. Q19 asks iteration counts for all five cases; Q13 permits reporting incomplete enhanced-RSM convergence behavior and significance. The previously transcribed FAQ instructions are confirmed. The other students' speeds and residuals in the questions are not values for this student's case.

## Current controls and actual initialization subsequently verified

The actual transcript now contains explicit `ACTUAL_RP` readbacks: flow/scheme=20 (SIMPLE), pressure/scheme=12 (second order), mom/scheme=1 (second-order upwind), pressure/relax=0.3, mom/relax=0.7, nut/relax=0.8, density/relax=1 and operating-pressure=101325 Pa. These resolve the earlier uncertainties for those controls without interpreting the conditional strategy map as current state.

The actual `/solve/initialize/hyb-initialization` command ran, with ten scalar iterations ending at 1.324414e-9 and explicit `Hybrid initialization is done.` The initialized Case/Data were written successfully as `case01_initialized.cas.h5` and `.dat.h5`. A separately saved configured case/settings includes the subsequently created force and mass-net monitor definitions. The remaining numerical-description readback is the S–A modified-viscosity spatial scheme and gradient scheme; neither should be inferred from the momentum order alone. Reference depth has an accepted actual depth=1 TUI command but no printed scalar readback yet.

During actual `/solve/iterate 1000`, Fluent stopped automatically at iteration 324 with `solution is converged` and residuals approximately continuity=9.8983e-4, x-velocity=4.4436e-7, y-velocity=9.4074e-8 and nut=4.2365e-7. This establishes fulfillment of the four configured 1e-3 solver stopping criteria only. Independent force stability, normalized mass balance, native exports and plots remain to be inspected before full Case 1 acceptance.

### Final readbacks and raw export inspection

Actual final `nut/scheme=0` confirms first-order upwind for S–A modified viscosity; momentum is second-order upwind and pressure second order. Actual gradient menu retains Least-Squares Cell-Based (Green-Gauss Node-Based=no, least-squares=yes). A failed query for undefined `rp-gradient` is preserved but does not invalidate the subsequent actual menu evidence. Do not describe all equations as second order.

Actual flux report reads inlet=9.352875 kg/s, outlet=-9.3528765 kg/s and net=-1.509178e-6 kg/s. The absolute net divided by inlet is approximately 1.6136e-7 as a fraction, or **0.000016136 percent**. State the denominator and percent/fraction explicitly. This agrees with the retained per-iteration mass-net monitor and the integrated prescribed inlet flow at one-metre depth.

Native surface exports each have 51 rows, but different hashes, coordinate sets, pressure and y-plus values. Inverse rotation maps every suction export point to positive foil-normal y and every pressure-side point to negative foil-normal y, confirming actual side separation. Suction pressure spans approximately -4032.98 to 26.95 Pa and y-plus 36.43–232.93; pressure-side pressure 63.36–1978.77 Pa and y-plus 17.71–150.46. The equal byte lengths arise from equal row counts/formats and are not evidence of duplication. These values still require model/wall-resolution interpretation; they do not prove spatial accuracy.

All three native velocity-line exports contain actual coordinates consistent with x=0.05,0.10,0.20 m (maximum recorded x deviation about 1.22e-8 m), spanning y=-0.075 to +0.075 m to export precision. Sample counts are 89, 91 and 40. The mid-chord export has the real foil-interior gap between approximately y=-0.01229241358 and -0.001665783226 m; plots must not join across it. The fixed x=0.10 m station is just downstream of this rotated baseline's actual trailing edge, so do not invent a solid gap there.

The dimensional force monitor includes 324 contiguous iterations. Final D=12.99779272904642 N and L=141.3685779316481 N imply CD=0.0819083070 and CL=0.8908636354 at the verified qS. Window range divided by absolute window mean is: last 25 iterations D=0.041215 percent, L=0.017169 percent; last 50 D=0.130990 percent, L=0.018514 percent; last 100 D=0.467264 percent, L=0.451292 percent. These measured drift diagnostics support describing a stable terminal force history at the reported precision, but are not an invented coursework threshold or proof of experimental agreement. Preserve the actual residual-criterion iteration count 324.

`case01_final.cas.h5`, `.dat.h5`, settings, journal/manifest, native histories and all formal surface/line exports are present and their writes are recorded. The exploratory `foil_surfaces.csv` followed an invalid `wall-yplus` command and contains pressure-only suction data; retain it as a failed/export-development attempt and use the two explicit p/y-plus files for analysis. Actual plotted-output review remains the final workflow gate before proceeding to the next case.

## Workflow acceptance and next-case release

The data agent's six final native-data figures were visually inspected: residuals, pressure, y-plus and all three velocity profiles. The residual threshold and terminal trend match the transcript; plotted pressure/y-plus correspond to actual separated sides; the mid profile is visibly split across the true solid gap. Updated integer axis ticks and source-preserving figures were inspected. Native `drag_breakdown.txt` and `lift_breakdown.txt` independently confirm pressure plus viscous forces on all three foil boundaries and agree with the monitor totals: drag pressure 11.414323 N plus viscous 1.5834696 N, and lift pressure 141.46217 N plus viscous -0.093590744 N. Their native coefficients match the independent normalization.

**Case 1 setup → solve → save → native export → traceable plots workflow passes independent review.** Solver was explicitly released to proceed with Case 2 and subsequent ordered cases without waiting for the user/main agent. Spreadsheet packaging and final Overleaf placement proceed independently and do not occupy the solver session. Any subsequent changes to plots or the report still need their applicable visual review.

This pass covers the evidenced prescribed setup, iterative criteria, terminal force/mass diagnostics and export integrity. It does not claim spatial convergence, transition-model adequacy, experiment matching or overall coursework completion. The large drag-coefficient discrepancy against the brief's reference must be analyzed rather than concealed; the prescribed coarse mesh, strongly confined duct, near-wall resolution and mixed equation orders remain model/numerical limitations.

Actual saved wall numerical settings are separately retained in `review/case01_wall_settings_audit.json`. Zero roughness height is explicit. A direct text-to-code readback for stationary/no-slip labels has been requested without delaying Case 2.
