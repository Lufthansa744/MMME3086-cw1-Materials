# Independent review of the enhanced-mesh runs

The original supplied mesh is retained unchanged with SHA-256 `3b823ee36532e037e1eb654a2306e9ad3e362d8bf60703ca0030ef85ae4bd47e`. Independent topology/geometry audit verifies 20,535 quads plus 39 triangles, 21,053 nodes, 41,627 faces, seven named physical boundary zones and two closed boundary loops. Actual Fluent check completes with minimum positive cell volume 9.467649e-10, minimum orthogonal quality 0.175206 and maximum aspect ratio 56.8411. These are valid imported mesh metrics, not proof of wall-treatment adequacy or spatial convergence.

## Initial enhanced RSM attempt

Actual inputs/model: RSM, EWT explicitly enabled, SIMPLE, 50.9 m/s, actual intensity 5 percent and length scale 1 m, original air constants and force references. It starts from the original mesh and independent hybrid initialization (ten steps, final scalar 4.727162e-10). Actual URFs remain pressure 0.3, momentum 0.7, k/epsilon 0.8 and Reynolds stresses 0.5. Momentum/pressure are second order, turbulence/stresses first-order upwind. The original log rather than a malformed first manifest RP entry establishes SIMPLE; the solver was asked to fix its formatting-token parser.

Fluent automatically stops at **432**, when all nine configured residuals first satisfy 1e-3. Epsilon values immediately preceding the stop are 0.0011628 at 430, 0.0013534 at 431 and 0.00091066 at 432. Therefore report **first residual-threshold crossing with preceding fluctuations**, not monotonic or sustained convergence and not a failed/divergent RSM attempt. The actual outcome must take precedence over an expected coursework narrative.

Final D=5.107296168 N and L=172.651504909 N give CD=0.0321846941 and CL=1.087999537. Last-25 force ranges divided by window mean are 0.1619 percent drag/0.2048 percent lift; last-50 are 0.3454/0.3334 percent, while last-100 drag range remains 1.3716 percent. Preserve these finite-window qualifications. Actual final net mass monitor is about -1.21149e-6 kg/s; normalized by the prescribed 9.352875 kg/s inlet this is about 1.2953e-5 percent.

All formal side/profile CSVs, TE wall export, complete signed cell fields, force/mass histories and final Case/Data are retained. Independent cell mapping verifies **20,574 unique cell IDs 1–20,574 with zero global offset**. Actual Fluent quad centres match vertex means within 3.85e-8 m; polygon area centroids can differ by up to 0.2498 mm and are not the matching export convention. All 413 foil wall faces (204 suction, 204 pressure, five TE) map by actual midpoint and adjacent cell ID to 413 unique cells; no multi-face cell merge is needed, and domain/wall y-plus values agree exactly. See `initial_enhanced_rsm_field_mapping_audit.json` and the reproducible generic mapping script.

## Prescribed Case 4 k–epsilon EWT

Actual k–epsilon plus EWT and SIMPLE are verified in the native transcript. It is independently hybrid reinitialized after switching from the retained initial RSM state, so this is not continuation of that RSM solution. Actual schemes are pressure/momentum second order and k/epsilon first order; URFs pressure 0.3, momentum 0.7 and k/epsilon 0.8. Physical/mesh/reference inputs remain unchanged.

All five residuals first satisfy 1e-3 at **215**: continuity 9.9029e-4, x velocity 2.8704e-6, y velocity 7.5806e-7, k 3.5874e-5 and epsilon 3.4207e-4. Final D=16.454434939 N and L=151.1801320 N imply CD=0.1036910602 and CL=0.9526931937.

**Material force-stability limitation:** drag is still decreasing, with last-25 range/mean 1.1638 percent, last-50 2.6019 percent and last-100 6.9054 percent. Lift ranges are 0.1287/0.3055/3.9352 percent. The residual stopping event is genuine, but drag is not stable at four-significant-figure accuracy. These terminal values should be labelled as residual-stop results unless a separately retained, consistently reviewed continuation establishes tighter force behavior. Main agent and solver were notified; this does not authorize overwriting the original Case 4 or the Case 5 seed.

Actual net mass monitor -4.218965e-6 kg/s corresponds to approximately 0.000045109 percent of prescribed inlet flow. Surface/profile exports are real and preserve fixed absolute stations and actual foil gaps. Content and source hashes are retained in `case04_raw_audit.json`.

## Case 5 comparison rules

Case 5 must retain its true lineage from the saved Case 4 solution. If it inherits global iteration 215, a displayed old 215/five-equation state and its convergence message are **not RSM iterations or RSM convergence**. Count the new nine-equation RSM solve from iteration 216; retain both terminal global index and added-RSM-iteration count. A seed record at 215 belongs to the inherited initial state and remains in the untouched native file but is excluded from added-RSM iteration statistics.

Compare the initial enhanced RSM and final relaxed RSM with the actual initialization history in view: independent hybrid versus continuation from a k–epsilon field. Differences cannot be attributed solely to URFs. Report true first-crossing/stability behavior and terminal statistics, not a presumed default-fails/relaxation-fixes story.

## Placement correction and final-report mapping

Provided enhanced foil placement is now strongly verified by shared side-zone LE/TE endpoints and NACA polynomial residuals below about 1.1e-9 m. The original baseline was displaced relative to it. Main agent has authorized a precisely translated **aligned baseline** and independent reruns of Cases 1–3, retaining the original prealignment runs as historical evidence. The final five-model comparison must use `_aligned` baselines; until those finish, the old baseline/enhanced force differences contain a removable geometry-placement confound. The enhanced meshes/runs themselves remain unchanged.

## Stricter verification subsequently authorized

Because Case 4 drag was still drifting materially at its first residual stop, the main agent has authorized a separate `case04_verified` continuation, preserving the 215-iteration early result. Its analyst-selected verification goal is all active residuals at or below 1e-5 **and** both drag/lift last-100 ranges divided by absolute window mean at or below 0.1 percent. Count 100 actual consecutive new-model updates, excluding inherited/duplicate report rows. This is a separately declared numerical acceptance target, not an assignment-specified threshold.

After stable Case 4 verification, rebuild `case05_verified` from that actual saved solution and apply the prescribed Case 5 model/URFs without hybrid reinitialization. Retain old early-seed Case 5 results only as diagnostics. Consistent final aligned baselines should use the same verification goal where attainable. If a prescribed RSM cannot meet it, retain settings and honestly report the actual terminal state, cap or fluctuation rather than manufacturing a pass.

Final report data need distinct first-1e-3 crossing index and verified terminal index, with forces explicitly tied to the latter. For Case 5 also retain the inherited global index and additional RSM iterations. The original iteration count 215 remains valid for the early Case 4 residual-stop event, but must not label forces obtained from a later verified state as if they were sampled at 215.

### Case 4 verified continuation accepted

`solver/case04_verified` actual transcript and configured/final settings verify reading the original Case 4 **Case and Data**, inheriting index 215, redirecting monitor files and tightening only residual stopping thresholds. No reinitialization occurs. Actual model, EWT, physical inputs, schemes and URFs are unchanged.

All five active residuals satisfy the declared 1e-5 verification threshold at **global 753**: continuity 9.9686e-6, x velocity 2.3250e-8, y velocity 5.1256e-9, k 3.7095e-7 and epsilon 2.7360e-6. Native monitor data contain one inherited seed row at 215, excluded from verification updates. There are **538 new KE updates**, while total KE iterations from its original independent initialization are 753. The original first-1e-3 event remains 215.

Independent last-100 actual-update calculations give range/absolute mean **0.0100644 percent drag** and **0.0554156 percent lift**, both passing the analyst's 0.1 percent target. Actual final D=15.61123397381552 N and L=143.9712236674034 N normalize to CD=0.0983774531 and CL=0.9072647514. The net mass monitor 8.062672e-8 kg/s is approximately 8.62053e-7 percent of prescribed inlet flow. Full native exports/retained source hashes and independently calculated windows are in `review/case04_verified_raw_audit.json`.

**Case 4 stricter iterative verification passes.** Solver was explicitly released to use this saved global-753 solution as the unique final Case 5 seed. Data agent was told to use the verified values/profiles in the final comparison and retain the earlier Case 4 workbook/results as early-stop evidence. Spatial/model/experimental validation remains separate.

### Case 5 verified continuation accepted

Actual native transcript proves loading verified Case 4 Case/Data and switching to RSM/EWT **without reinitialization**. Both retained seed-file SHA-256 values still match the Case 4 verified originals. Actual menu/RP readbacks give momentum/k/epsilon/turbulent-viscosity URFs 0.5, Reynolds stresses 0.25, pressure 0.3 and density/body force 1. SIMPLE and existing physical inputs/schemes remain unchanged.

The old inherited index 753 and its convergence marker are excluded from RSM updates. Native history contains exactly **2,936** consecutive new iterations 754–3689. Independent scanning of the nine-equation rows finds the first all-residuals <=1e-3 at global **1737**, or **984 added RSM iterations**. The strict all-residuals <=1e-5 crossing is global **3689**, or **2936 added RSM iterations**. At the strict stop, continuity=9.9828e-6 and epsilon=7.9895e-6 are the largest residuals; all nine pass.

Last-100 actual RSM-update force ranges/absolute means independently calculate **0.04807275 percent drag** and **0.06402909 percent lift**, passing the declared 0.1-percent target. Final D=5.232899341976225 N, L=158.8477374876382 N normalize to CD=0.0329762087, CL=1.0010122119. Net mass monitor is approximately 7.43331e-8 kg/s, about 7.94762e-7 percent of prescribed inlet flow.

Complete native fields and all 413 foil-adjacent cells again match the original enhanced mesh IDs/centres/face adjacency, zero global offset, actual quad vertex-mean centres and identical wall/domain y-plus values. Initial stress export confirms normal stresses approximately 2k/3 to ASCII precision and uv=0. Final stress traces remain consistent with 2k to relative error below 7.4e-10; all normal variances and in-plane covariance eigenvalues are positive in the exported cells. These basic consistency checks do not prove closure accuracy.

The final combined Figure 6 was independently viewed after field-mapping validation. Panel (a) has actual signed vectors and wake, while panel (b) is an explicitly linked, true equal-aspect maximum-y-plus local zoom without exaggerated cell thickness. Speed scale 0–120 m/s covers all selected vector speeds (maximum about 97.90 m/s; full-domain maximum 108.02 m/s). All 413 foil wall values span **0.14730–6.58591**; 57 are <=1, 354 are in (1,5] and two exceed 5. Do not claim all cells have y-plus <=1 or infer mesh adequacy merely from these values. Legend and the actual maximum cell annotation 6.59 are correct.

**Case 5 final numerical/native-data/Figure 6 workflow passes the stricter independent review.** Raw statistics, source hashes, mapping and seed/stress checks are in `case05_verified_raw_audit.json`, `case05_verified_monitor_audit.json`, `case05_verified_field_mapping_audit.json` and `case05_verified_stress_seed_audit.json`. Old early-seed Case 5 remains historical evidence and must not replace these final values or iteration counts.
