# Independent quality status

This file tracks review disposition, not a submission report or a claim that unfinished runs have passed.

## Current final-run mapping

| Final report item | Intended retained source | Independent status |
| --- | --- | --- |
| Task A geometry and baseline mesh | `solver/aligned_taskA` | CAD coordinates/shared LE/TE, kernel hole, native topology and Fluent quality pass; aligned compact Fig1/2 source and independent image review pass; eventual Overleaf placement remains |
| Case 1 S–A | `solver/case01_aligned` | Strict numerical/raw/field/figure chain passes at 489; first 1e-3 at 293 retained; original `case01` is prealignment history |
| Case 2 standard k–epsilon | `solver/case02_aligned` | Qualified acceptance at cap 2225*: first 1e-3 at 225; strict continuity target unmet (4.0118e-5); integral forces/mass stable; hash-bound acceptance in case02_aligned_qualified_acceptance.json |
| Case 3 baseline RSM | `solver/case03_aligned` | Qualified acceptance at cap 2919*: first 1e-3 at 419; strict continuity unmet (2.8063e-4), force target passes, real field mapping and fresh Fig4/5 independent visual review pass |
| Initial enhanced RSM diagnostic | `solver/initial_enhanced_rsm` | Actual first-1e-3 crossing at 432 verified; preceding epsilon fluctuations and remaining force drift retained; not a failed attempt or final Table 1 case |
| Case 4 k–epsilon EWT | `solver/case04_verified` | Strict iterative target passes at total KE iteration 753; first-1e-3 at 215 retained separately |
| Case 5 relaxed RSM EWT | `solver/case05_verified` | Strict numerical/export/field/Figure 6 workflow passes at global 3689, 2936 added RSM iterations from verified KE753; first1e-3 at global1737/additional984; older early-seed Case 5 is diagnostic history |
| S–A grid check | Three aligned mesh levels with identical non-mesh settings | Three aligned levels independently verified; all S-A iterative gates pass. CD still changes 4.787% medium-to-fine and CL is nonmonotonic; no spatial independence accepted |
| k–epsilon inlet-L contrast | Aligned Case 2 L=1 vs independently retained L=0.01 | Completed separate qualified sensitivity at 2500 cap; same mesh/closure/material/BC except L verified; both L branches retain strict continuity limitations |

## Material issues found and corrected

- Native geometry/mesh checks established the foil hole and seven actual named boundaries; numerical counts were verified from native files, not text claims.
- Independent NACA/endpoint analysis discovered that the original baseline was displaced relative to the supplied mesh. A pure translation was verified to roundoff and a new aligned CAD/mesh is accepted. Original solved fields cannot be translated or reused as aligned results.
- Equal-length suction/pressure exports were shown to have distinct hashes/coordinates/values and correct side identity. Real line coordinates and solid gaps were checked.
- The enhanced field-cell mapping was checked against actual mixed quad/triangle geometry. Correct cell IDs have zero global offset; actual quad export centres use vertex means, not polygon-area centroids. No blind multi-face averaging is needed in the inspected original enhanced diagnostic.
- First residual crossing was separated from force stability. Case 4's early drag continued changing materially, prompting strict continuation. Verified Case 4 now meets all active residuals <=1e-5 and both last-100 force range/absolute mean <=0.1 percent, the declared analyst target.
- Case 5 seed/global indices are separated from added RSM iterations. Inherited five-equation rows and old convergence markers cannot be counted as RSM convergence.
- Actual model-specific first-order turbulence/stress schemes are recorded, avoiding a blanket second-order claim. Actual S–A selector behavior follows the FAQ oversight clarification.

## Final numerical and physical limitations still requiring honest reporting

All report forces must identify their actual source terminal state and suitable precision. The stricter 1e-5/0.1-percent goals are analyst-selected verification standards, not fabricated assignment thresholds; first-1e-3 event indices remain separately meaningful. A prescribed RSM run that misses the target must be reported as such.

The three-grid study is necessary before any spatial-convergence claim. Model changes plus near-wall treatment changes between the five prescribed cases cannot isolate grid error. Observed nonmonotonic/nonasymptotic behavior does not justify an invented formal order or forced GCI.

The retained 5-percent inlet intensity and 1 m selected length scale are actual software inputs, not measured tunnel turbulence. Actual RSM inlet exports show k=9.71554, epsilon=30.2831 and turbulent/molecular viscosity ratios about 6261–19167. These cannot be relabelled as experimental or S–A/k–epsilon inlet observations. The independent length contrast can quantify sensitivity to an input assumption, not establish a true experimental value.

The confined CFD duct has H/c=1.5, while the reference test geometry is around H/c=14. Corrected experimental section data with inserts/end plates do not duplicate the narrow-duct CFD conditions. Fully turbulent closures and differing inlet/transition conditions remain model-form/physical-representation limitations even when residuals and mass balance are excellent.

The specified original-brief graph readings CL approximately 0.81 and CD approximately 0.017 at 8 degrees are verified graph estimates with visual allowances, not exact tabulated ordinates. Keep source identity and graphical reading precision; do not silently replace them with readings from a different primary Sandia figure. A small coefficient error can conceal compensating errors.

Final report layout/page count must be checked only from the permitted Overleaf compile. Four approved section headings and displayed-equation punctuation must remain intact. The supplied nine-page brief requests an eight-page report and an AI-log appendix of at most two pages but omits its referenced official Appendix 1/seven-point template and explicit appendix page accounting. Actual current assistance should be disclosed accurately; these source gaps are not permission to invent official requirements or claim an uncompiled PDF is ready.

## Latest aligned run dispositions

Case 1 aligned: native D=12.8107950446 N, L=142.1325101743 N; CD=0.0807299020, CL=0.8956777141. Four final residuals meet 1e-5. Last-100 range/mean D=0.00828572%, L=0.00210524%, within analyst 0.1% target. New source plots and real cell/wall mapping independently pass.

Case 2 aligned: native D=14.3051490954 N, L=131.1228002486 N; CD=0.0901468863, CL=0.8262977263. Native first default crossing 225 is valid, including an identical non-update transcript reprint. Final 2225 stops at the predeclared extension cap. Continuity is 4.0118e-5 across the last 100 printed iterations; other residuals are below 1e-5. Last-100 D/L range percentages are 0.00001325085/0.00000041456; net flux alternates approximately +/-5.4214e-8 kg/s. Qualified inclusion is authorized with strict gate FALSE and explicit report limitation. Integral stability does not prove local continuity or a floating-point cause. Native source hashes bind review/case02_aligned_qualified_acceptance.json to the accepted final state.

Case 3 aligned qualified source review: first default 1e-3 at 419, final cap 2919; nine final residuals except continuity are below analyst 1e-5. Last-100 continuity spans 2.8063e-4 to 2.8103e-4; force range/mean D=0.00534958%, L=0.00489643%. D=8.4276210521 N, L=120.7250519682 N, CD=0.0531084152, CL=0.7607741427. Actual entire-domain signed u is positive (minimum 1.612503047 m/s); old prealignment reverse-flow observations must not be reused. Qualified source contract is case03_aligned_qualified_acceptance.json, independent actual raw and field audits retained. Cell mass-imbalance units/definition remain unconfirmed and are not used to overrule the strict residual miss.

All five final wall-length y+ coverage datasets were independently recomputed using review binary mesh readers and native face scalar exports. Each actual wall-face length, midpoint, adjacent cell ID and y+ was checked; all six coverage fractions match within 1e-13. See wall_length_coverage_audit.json. Final aligned Case 3 Fig4/5 images independently pass: actual positive signed streamwise field, correct normalized-direction inset label, actual mesh cells and low-y+ highlights.

## Additional verification progress

Medium aligned S-A mesh native topology/alignment/quality pass (12410 triangles, h_eff=0.003467106573 m). Its independent hybrid run meets all four 1e-5 residuals at 737 and the last-100 force range target (D 0.00868096%, L 0.00985276%). CL=0.9146569581 and CD=0.0723818398. Fine mesh geometry/topology/Fluent quality also passes (20195 triangles, h_eff=0.002717882835 m); fine solution passes all four 1e-5 residuals at 1016 and both last-100 force targets (D 0.00967728%, L 0.01254096%). Do not claim spatial independence from the medium result.

Local mass-imbalance fields for final aligned Cases 2/3 are now dimensionally confirmed by actual native Mass Imbalance [kg/s] report and independently mapped across all 7687 cells. Case 2 max absolute value 6.34298e-7 kg/s and sum of magnitudes 9.84757e-6 kg/s (0.000105289% inlet); Case 3 corresponding values 1.07860e-6 and 3.92661e-5 (0.000419830%). Signed sums agree with global flux. These supplement the qualified acceptance and distinguish cancellation from total local imbalance; they do not change strict residual flags or establish a plateau mechanism. Full evidence in local_mass_imbalance_audit.json.

Fine S-A final CL=0.9117482709, CD=0.0689165913. Real adjacent refinement ratios come from h_eff=sqrt(actual fluid area/N), not nominal sizing. CD decreases 10.3407% coarse-to-medium and 4.78746% medium-to-fine. CL changes +2.11898% then -0.318009%; this nonmonotonic three-level lift and appreciable drag sensitivity do not support a grid-independent five-case accuracy ranking. All refined cell/wall IDs, coordinates, adjacency and native y+ match their respective meshes. Actual spatial changes exceed the inspected terminal iterative force-window ranges. No formal order or GCI is approved.

Final Workbench five-system imported case/data H5 pairs were independently hashed byte-for-byte against the ten actual final source files; all ten match. See workbench_import_hash_audit.json. This establishes the stored copies, not a screenshot claim about a live UI.

## Inlet-length contrast final disposition

The independent aligned k-epsilon L=0.01 m run is qualified auxiliary evidence, not an extra entry in the prescribed five-model table. All nine saved BC blocks compare identically to final aligned Case 2 except inlet turbulent length scale, and material definitions are byte-identical. Native journal/readback confirms the same numerical controls and independent Hybrid initialization without importing baseline data. Fresh 7687 cell/103 wall mapping passes. Default residual crossing is 332; at cap 2500 continuity remains 7.635e-5, above analyst 1e-5, while other active residuals and force-window targets pass. Hash-bound disposition is sensitivity_ke_length_001_qualified_acceptance.json.

Relative to final aligned L=1 Case 2, CD changes from 0.0901468863 to 0.0605702906 (-32.8093%) and CL from 0.8262977263 to 0.7767620625 (-5.99489%). This is much larger than either terminal integral-force window range. It quantifies sensitivity to an analyst-selected inlet assumption in this mesh/closure/duct setup; it does not identify experimental turbulence, validate L=0.01 m, remove spatial error, or justify selecting a value because it approaches one coefficient. Both compared branches retain strict continuity limitations, so precision and qualified status remain explicit. Actual inlet export k is unchanged at 9.7155375 m2/s2 and epsilon changes 30.28309428 to 3028.309428 m2/s3. Derived turbulent-viscosity values are native inlet-surface cell-centred outputs, not a direct proof of prescribed uniform transported viscosity.

## Final source disposition

Final report source/content independently accepted at main.tex SHA256 d3c118e2faaaa9d281edd0aee3d9e4f2d4394ec59a97dcc71382c1e0bfec6cc8, with 13 final asset hashes and verified table checked. C4 approximately 450 conservative source words is below 550; individual earlier question limits also pass. Review does not claim Overleaf upload/compile, final page count or rendered layout acceptance. These remain outstanding under the user-only-Overleaf constraint and the parent-reported site permission denial. Full final source assessment is final_report_content_review.md and final_report_source_audit.json.


Latest print package supersedes the earlier PNG-only source snapshot: main SHA256 93391df3f80c4e90e85a5af5c1f13c2fbd26d03f4823f23ecbadc02831a34898, source ZIP SHA256 527ef3cc1616a087a4b57c23a75a55348ba6d9c5bf577c5c1eb63bb961aaad95. Figures 3-13 use corrected embedded-font vector PDFs, all independently parsed/rendered/source-compared; 1-2 preserve original native/mesh PNGs. All 20 ZIP members match prepared sources. Approved class is unchanged; natural pagination replaces seven manual breaks. Final report rendering and page count still require permitted Overleaf compilation. See layout_and_vector_review.md, vector_pdf_independent_audit.json and final_print_package_audit.json.
