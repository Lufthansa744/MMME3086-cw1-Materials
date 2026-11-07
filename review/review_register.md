# Independent review register

## Authority and evidence

This register records the user's instructions and discovered sources. It is an internal audit record, not report prose. Review status is **not assessed** until actual solver settings, results, and the CFD brief are available.

- Student ID: 20617209, supplied by the user
- Inlet speed: 50.9 m/s, supplied by the user
- Other fluid properties and turbulence parameters: must be read from actual case settings
- Solver ownership: solver agent exclusively controls Fluent
- Order: validate local Fluent, finish Task A, complete Case 1 from setup through plots, then proceed in question order and attempt the initial enhanced RSM case
- Every case must retain independent settings, logs, Case/Data, monitors, and raw exports
- Report values must be traceable to retained raw data
- Retain the previously approved AIAA template and required sections
- Compile only in Overleaf
- Submitted prose must not contain `working draft` or `TODO`
- No punctuation following displayed equations

## Discovery results

Read-only filename search performed over:

- `C:\Users\A320N\Documents\ChatGPT`
- `C:\Users\A320N\Desktop`
- `C:\Users\A320N\Downloads`

Excluded `.git`, `.venv`, and `.tools` paths in the focused search.

| Discovered file | Assessment |
| --- | --- |
| `C:\Users\A320N\Downloads\MMME3086-NM-Coursework-2526 - Template.docx` | Text identifies Numerical Methods coursework, Matlab finite-volume temperature solutions; not a CFD assignment authority |
| `C:\Users\A320N\Downloads\CourseWork 1.docx` | Text identifies AERO2003 quadrotor controller coursework; unrelated |
| `C:\Users\A320N\Downloads\new-aiaa.cls` | AIAA class file exists; approved report source and sections remain unverified |
| `C:\Users\A320N\Downloads\new-aiaa.bst` | Bibliography style exists; does not establish approved report contents |

No CFD brief or Fluent `.cas`/`.msh` file was identified by the focused filename search in these three roots. This does not establish absence elsewhere, inside archives, or in connected/browser sources.

An additional read-only filename search of `C:\Users\A320N\Documents\Codex` found no `AGENTS.md`, CFD coursework, TeX/PDF brief, or Fluent case/mesh/journal among returned filenames. An unrelated `2026-10-26\windows-2\work\nailong-7.zip` archive was not opened.

## Case 1 review gate

The following are evidence checks, not invented numerical coursework criteria. Numerical acceptance thresholds must come from the actual brief or a justified, recorded analysis.

| Check | Evidence needed | Status |
| --- | --- | --- |
| Case identity and task mapping | CFD brief, case label, geometry/angle/mesh and requested model | Not assessed |
| Mesh | Mesh file identity/hash, dimensions/units, zones, quality report and checks | Not assessed |
| Models | Actual solver settings, dimensionality, steady/transient, pressure/velocity coupling, turbulence and wall treatment | Not assessed |
| Boundary and material settings | Actual inlet velocity, direction, turbulence parameters, density/viscosity law and outlet/wall conditions | Not assessed |
| Reference values | Actual reference density, speed, length, area/depth, pressure and force directions | Not assessed |
| Numerical controls | Discretization schemes, relaxation or equivalent controls, initialization and iteration history | Not assessed |
| Residual behavior | Full raw histories, criteria and terminal window | Not assessed |
| Force behavior | Raw force/coefficient monitors with iteration/time, terminal statistics and drift/oscillation | Not assessed |
| Conservation | Actual inlet/outlet mass flow values and normalized imbalance with stated denominator | Not assessed |
| Wall resolution | Actual y-plus distributions/range and relation to the chosen wall treatment | Not assessed |
| Results and physical interpretation | Pressure/velocity/wall distributions, force decomposition, requested comparisons and expected mechanism checked against actual fields | Not assessed |
| Coefficient traceability | Dimensional forces, reference dynamic pressure/area and coordinate transform if applicable | Not assessed |
| Provenance | Settings, launch journal/script, transcript, final Case/Data, raw exports and metadata | Not assessed |
| Plot traceability | Reproducible script, raw input paths/hashes and plotted quantities/units | Not assessed |
| Report readiness | Approved template/sections, evidence-backed prose, equation punctuation and Overleaf compile | Not assessed |

## Current blockers to substantive review

1. Original CFD assignment PDF is not yet on Windows; task definitions have now been recovered as prior Mac command outputs (see below).
2. Actual case/mesh and its material/boundary/model settings are not yet available.
3. Approved AIAA report source, prescribed sections and Overleaf project identity are not yet verified.
4. Main agent reports that Overleaf currently presents a login page. Authentication and project identity must be supplied or completed before Overleaf editing and compilation can proceed.

Do not report numerical convergence, mesh independence, physically validated results, or coursework completion before the corresponding evidence is reviewed.

## Recovered assignment evidence

The main agent recovered actual prior Mac command outputs from chat `01a1ae21-c25b-7a70-a293-a810c5f7b17a`. These are source-text excerpts, not the original PDF/Word documents or their figures. They support task mapping but do not provide omitted diagrams, exact coordinates or omitted appendices.

- `coordination/recovered/brief_pages1_8_recovered.txt`: assignment pages 1–8, partial page 8
- `coordination/recovered/task_ABC_recovered.txt`: task pages 6–8 and beginning of page 9
- `coordination/recovered/word_template_recovered.txt`: original Word template text and headings
- `coordination/recovered/mesh_teaching_recovered.txt`: practical mesh teaching pages 1–8

### Task A acceptance

| Item | Exact recovered requirement | Review status |
| --- | --- | --- |
| A1 geometry | Own 150 mm by 1 m duct with NACA0012 at 8 degrees; Figure 1 and short descriptive caption | Not assessed |
| A2 mesh | Triangular cells, duct sizing 10 mm, only aerofoil-wall sizing 2 mm, growth rate 1.05 away from aerofoil | Not assessed |
| A2 illustration | Figure 2 with local aerofoil inset and caption under 100 words explaining mesh consideration in CFD theory | Not assessed |
| A3 boundaries | Appropriate names for all boundaries, labelled in Figure 2 | Not assessed |
| Method provenance | Assignment specifies Discovery and Ansys Mesher, using step-by-step consolidation method | Not assessed |

The teaching example duct on page 3 is 1000 mm by 100 mm. The assignment's 150 mm height is the controlling value. The excerpt does not establish aerofoil axial placement or rotation centre. Record actual geometry coordinates and derive sampling lines from the actual chord and trailing edge, rather than guessing their absolute x values. The teaching text calls the fluid shape a surface body, instructs checking Fluid material designation, and uses Workbench Fluid Flow (Fluent), explicitly excluding the Fluent-with-Fluent-Meshing workflow for that practical. It instructs named inlet/outlet and wall1/wall2 boundaries and updating the mesh to pass it to Fluent.

### Task B and case mapping

- B0 requires actual air density, viscosity, inlet turbulence intensity and isotropic RMS fluctuation velocity, inlet velocity and chord-based Reynolds number. Chord is 100 mm. The speed calculation with the last two ID digits is `(9/100)*10+50 = 50.9 m/s`, consistent with the user's value. Actual property and inlet settings remain unread.
- Case 1: Spalart–Allmaras, assignment-described standard wall function, SIMPLE, initialize and run to convergence. Figure 3 residual history and caption interpreting convergence; report criterion and iteration count. Verify the actual wall treatment exposed by Fluent 2022 R2 for S–A and record its real setting; do not merely repeat an unsupported UI label.
- Case 2: same mesh, k–epsilon, standard wall function, SIMPLE; duplicate method in Workbench is specified.
- Case 3: same mesh, RSM, standard wall function, SIMPLE; Figure 4 velocity vectors including wake, force/criterion/iteration reporting; Figure 5 aerofoil-adjacent cell y-plus values, visible legend and interpretation of unusual regions against the selected wall function.
- All cases: export static pressure and y-plus separately for suction and pressure sides; velocity magnitude across the duct at mid chord, trailing edge and 100 mm downstream of trailing edge; retain lift and drag, convergence criterion and iteration count. An Excel spreadsheet is requested.
- B3 initial enhanced RSM attempt: load the supplied `Aerofoil8-degAoA-enhancedBL.msh`, RSM, enhanced wall treatment and SIMPLE; retain and state the observed behavior.
- Case 4 after initial attempt: enhanced mesh, k–epsilon, enhanced wall treatment, SIMPLE; retain convergence rate and all B1 data.
- Case 5: duplicate and switch to RSM, Reynolds-stress under-relaxation 0.25, all other turbulent and momentum under-relaxation parameters 0.5; continue until convergence or no change. Retain forces, residual behavior, data and comparison of the two enhanced RSM attempts. Figure 6 contains velocity vectors and y-plus for the enhanced RSM result.

Use distinct identifiers for the initial enhanced RSM attempt, final Case 4 k–epsilon, and Case 5 RSM so no original run is overwritten or mislabelled.

### Task C and report structure

- C1: three cross-duct velocity comparison graphs for all models; each explanation below 100 words, with model/mesh reliability considered.
- C2: two static-pressure graphs, one for each aerofoil side, across all five cases; each explanation no more than 100 words, with reliability considered.
- C3: two y-plus graphs across models; combined explanation below 100 words, with reliability considered.
- C4: compare 8-degree lift/drag coefficients to supplied Sheldahl validation plot; discussion below 550 words including Reynolds number, confinement/physical setup, accuracy, reliability and why matching experiment matters. Use planform area with 1 m depth; with recovered chord 0.1 m this is 0.1 square metres, subject to confirming actual geometry. Brief quotes Sheldahl test chord 150 mm, span 900 mm and tunnel height 2.1 m; verify these from the actual cited paper before external factual claims. The experimental plot is not present in the recovered text.
- Word template section headings: `Task A Geometry [16]`; `Task B Solution and data extraction [34]`; `Task C Analysis [50]`; `Task C Boundary Conditions and Results` (the latter contains C4). Preserve these contents and required Figure 1–13/Table 1 mapping within the user's already approved AIAA structure; do not replace that approved template.
- Word template additionally limits B3 description to 150 words and Figure 6 description to 150 words. It asks for Table 1 containing lift, drag, iterations, CD and CL for S–A, k–epsilon, RSM, k–epsilon Enhanced and RSM Enhanced.
- Brief states an eight-page report and an AI-usage appendix of at most two pages addressing seven points, plus an AI guidance table. The actual seven-point template and appendix guidance table are absent from recovered excerpts; do not invent their prescribed contents. Whether the appendix counts in the eight pages remains unverified.
- Recovered deadline: 12 November 2026, 15:00; PDF naming convention `Last-name_First-name_Student-ID-number_CFDAssignment.PDF`.

## Independent local startup evidence review

Read-only inspection of `solver/validation/verify.jou`, `validation.transcript`, and `launch-native.log` confirms the native journal was read and executed to the marker `MMME3086_JOURNAL_INTERFACE_OK`, followed by a clean transcript stop and exit. The launch log identifies ANSYS Fluent 2022 R2, build 10212, license server `1055@localhost`, and license support for four-way parallel execution. The transcript identifies executable `D:/ANSYS Inc/v222/fluent/ntbin/win64/fluent.exe`. This demonstrates solver startup and Scheme/journal execution only; no CFD case, material settings, actual numerical solve, export or convergence has yet been reviewed.

## Geometry teaching pages 9 through 14

Source: `coordination/recovered/mesh_teaching_full_truncated.txt`, recovered prior command output. The final page is truncated.

- The teaching formula is the NACA0012 thickness distribution with coefficient `-0.1015*t^4`, dimensional coordinates `x=100*t` mm and `y=500*0.12*(...)` mm, with `t` from 0 to 1. Retain this finite trailing-edge definition rather than silently replacing its coefficient with a closed-edge variant.
- Page 10 explicitly instructs connecting the upper and lower trailing-edge endpoints, filling the aerofoil and subtracting it from the duct. Check that the trailing-edge connector is also part of the aerofoil force-zone selection and a no-slip boundary. If suction/pressure profile exports omit that connector, the total force must still include it and its treatment must be documented.
- The rotation instruction allows 8 or 352 degrees depending on orientation. This is a UI orientation hint; assess the actual relative inlet-flow direction and LE-to-TE chord direction, as well as lift/drag signs. The displayed rotation number alone does not establish the physical angle of attack.
- The appendix uses duct corners `(-500,50),(-500,-50),(500,50),(500,-50)` mm, a 100 mm-high example. For the required 150 mm duct, a centreline-symmetric version would instead use y=+/-75 mm, but actual constructed coordinates must be inspected.
- Page 12 uses teaching mesh sizes of 5 mm global and 0.5 mm aerofoil; assignment sizes of 10 mm and 2 mm control Task A.
- Page 13 describes direct mesh import via a Workbench Fluent Component System. The original enhanced mesh is still required for B3; reconstructing an assumed equivalent does not verify use of that supplied file.

## Independent force processor review

Files inspected: `data/process_forces.py`, `data/README.md`, `data/export_and_figure_map.md`.

Accepted implementation points:

- Coefficients use Cartesian total-force projections divided by `0.5*rho*U^2*S`, with positive finite rho/U/S.
- Drag/lift directions must be unit vectors and mutually perpendicular. No global axis or angle rotation is assumed.
- Reference speed is constrained to the authorized 50.9 m/s; there are no density/area defaults.
- Actual-case evidence file existence, locators and hashes are recorded, while the README correctly states that matching the values to the evidence still requires review.
- Iterations must strictly increase and restarted histories must be split explicitly.
- Retained history and last-window mean/range/trend do not claim numerical convergence.
- Raw force CSV is read only, and prior processing output directories cannot be overwritten.

One material provenance issue was found in the reviewed version: native Fluent force exports and conversion scripts/mappings were only optional evidence. A manually converted Cartesian CSV could therefore yield an apparently complete audit while omitting the native source hash and how native columns, units and signs became `Fx_N,Fy_N,Fz_N`. Requested correction from the data agent: require native force source evidence and an explicit conversion record (identity when the CSV itself is the direct native export; otherwise recorded conversion script and column/unit/sign mapping). Until corrected and checked, the processor provides traceability to its input CSV but does not mechanically guarantee traceability back to Fluent's original export.

No actual numerical result, report coefficient or simulation acceptance is approved by this code review.

### Provenance correction review

The data agent's updated `process_forces.py`, `README.md`, and six-case `test_provenance.py` were independently inspected. The previously identified missing-source issue is **resolved at the metadata and evidence contract level**:

- `native_force_source` is mandatory in `load_metadata`, with existing-file resolution, nonempty locator and recorded SHA-256.
- `verify_conversion` is invoked before processing and requires `identity` or `script` mode, with source, expression, source units and target units for iteration and all three force components.
- Identity conversion requires matching native/CSV byte hashes and unchanged columns/units.
- Script conversion requires hashed conversion-script evidence and a separately retained native file.
- The audit retains metadata (including conversion mappings), evidence hashes, input/script hashes and output hashes.
- The six tests cover missing native source, missing mode, missing mappings, missing mapping fields, byte identity and transformed-source preservation. The data agent reports all six passed; no redundant rerun was required after read-only review.

The remaining acceptance work is deliberate independent review of the actual evidence: force zones, pressure-plus-viscous totals, physical units/signs/depth, actual-case normalization inputs, and correctness/reproducibility of a conversion script. Merely preserving a script does not prove its output came from the recorded native file; the documentation correctly limits that claim. No further material implementation defect was found in the reviewed update, and no CFD result has yet been supplied for numerical validation.

## Actual Task A geometry review

Read-only inspection covered `solver/taskA/create_geometry.py`, `geometry_properties.txt`, `boundary_edges.csv`, `foil_coordinates_m.csv`, `geometry_creation.txt`, and the saved `taskA_geometry.scdoc` package. Reproducible calculations and source SHA-256 hashes are in `review/verify_geometry.py` and `review/taskA_geometry_audit.json`.

**Accepted from actual saved evidence:**

- Outer boundary endpoints are x=-0.5 to +0.5 m and y=-0.075 to +0.075 m, giving the required 1 m length and 150 mm height.
- There are 401 actual sample coordinates per side (802 rows), with maximum inverse-rotation error against the recovered NACA0012 formula of approximately 6.1e-16 m. This checks the coordinate inputs, not a separately measured bound on the CAD spline interpolation error. The construction requests a 1e-7 m through-points spline tolerance.
- Leading edge is (0,0); mean trailing-edge point is (0.099026806874157,-0.013917310096007) m. The inferred chord is 0.1 m and its geometric orientation is -8 degrees. Relative to a +x inlet this gives positive 8-degree aerodynamic angle of attack; the actual inlet remains to be verified in Fluent.
- The finite trailing-edge thickness is 0.000252 m. The endpoint export contains an explicit `aerofoil_te` connector between the two endpoints. Maximum sampled unrotated thickness is approximately 0.01200334 m, consistent with the specified NACA thickness formula.
- Actual geometry log records one face and seven edges. All seven boundary names (`inlet`, `outlet`, `wall_top`, `wall_bottom`, `aerofoil_suction`, `aerofoil_pressure`, `aerofoil_te`) appear as distinct `NamedSelectionDef` entries with object references inside the saved SCDOC XML. This verifies name persistence in the geometry document, beyond just the CSV labels.
- Derived full-duct profile stations, if using chord midpoint and mean trailing-edge x coordinates, are x=0.0495134034370785, 0.099026806874157 and 0.199026806874157 m. Use actual endpoints y=-0.075 to +0.075 m and retain the definition; the middle line uses the centre of the finite-thickness trailing edge.

**Still unverified:**

- One face with seven boundary edges is strongly consistent with a duct face containing an aerofoil hole, but the supplied text does not directly report face loops, kernel surface area or point membership. Requested solver-owned follow-up: surface area (expected approximately 0.1491779083 square metres from sampled-polygon area) and fluid/foil point-membership or loop evidence. This value is an independent polygon approximation, not a kernel measurement.
- The saved thumbnail was inspected but shows an oblique small view dominated by axes; it is not adequate visual evidence of the hole or a submission-ready Figure 1. A clear top view with dimensions remains necessary.
- Mesh sizing, mesh quality, boundary-name transfer into Mesher/Fluent, actual fluid designation and the task's Figure 2/inset remain unverified. Task A is therefore not yet complete.

No Fluent or Workbench session was accessed by the reviewer.

### Kernel hole evidence received

The solver's `geometry_kernel_audit.txt` and `audit_geometry.py` were independently read. The script reopens the saved SCDOC and interrogates the actual body. It reports one face, seven edges, **two face loops**, fluid test point membership true, and an aerofoil-interior test point membership false. These close the outstanding hole-topology gate.

Kernel surface area is 0.14917724490682 square metres. Integrating the specified NACA thickness polynomial analytically gives foil area 0.0008221 square metres and fluid area 0.1491779 square metres. The kernel discrepancy is about 6.55e-7 square metres (0.00044 percent of duct-fluid area; 0.080 percent of foil area). The 401-point construction polygon differs from the analytic foil integral by only about 8.3e-9 square metres, so polygon sampling alone does not explain the larger kernel difference. This is not currently grounds to rebuild a valid geometry, but it prevents assigning the construction tolerance as a measured CAD-curve error bound. Requested solver-owned dense sampling of the actual saved CAD edge curves to distinguish interpolation deviation from kernel area-integration accuracy; do not stop meshing solely for this diagnostic.

The data agent's `data/taskA/geometry_coordinate_check.png` was visually inspected. It provides a readable equal-scale coordinate reconstruction of the actual exported inputs and boundary labels. It is supplementary audit evidence rather than a Discovery screenshot or proof of the meshed CAD domain; the native geometry view remains preferred for Figure 1.

### Actual CAD edge sampling follow-up

`solver/taskA/cad_edge_dense_coordinates_m.csv` contains 1001 points for each of the three actual CAD aerofoil edges. Results and original-file SHA-256 are retained in `review/cad_dense_audit.json`. Independently inverse-rotating those actual curve points gives maximum thickness-formula deviation about 7.42e-7 m on each surface very near the leading edge (unrotated x about 3.24e-6 m). The dense CAD boundary polygon gives foil area 0.0008220985003 square metres, within approximately 1.5e-9 square metres of the analytic polynomial integral. This strongly supports the intended actual CAD shape and does not reproduce the much larger kernel area discrepancy. Kernel integration accuracy is a reasonable explanation, rather than a demonstrated shape error; retain the actual geometry and proceed. Do not describe the requested 1e-7 m fitting tolerance as a measured maximum curve error.

### Original enhanced mesh now retained

The original `inputs/Aerofoil8-degAoA-enhancedBL.msh` was read without modification. It contains 1,086,513 bytes and SHA-256 `3b823ee36532e037e1eb654a2306e9ad3e362d8bf60703ca0030ef85ae4bd47e`, matching `inputs/provenance.json`. Independent native-header parsing verifies nodes=21,053, cells=20,574 and faces=41,627. Zone records verify `aerofoil-pressure`, `aerofoil-suction` and `aerofoil-trail` are wall zones, together with declared velocity inlet, pressure outlet and duct roof/floor walls. The corresponding old-report count and zone-name assertions are now supported by the actual retained original mesh. Header parsing is not a quality check, actual boundary-value/model read, solver import or solved result. `review/verify_enhanced_header.py` and `review/enhanced_header_audit.json` retain the reproducible inspection.

## FAQ clarification reported from the user's screenshot

The main agent supplied the following user-provided FAQ clarifications on 7 November. The image is expected at `inputs/FAQ_2026-11-07.png`; independent visual confirmation was pending when this entry was written. They supersede earlier ambiguous brief interpretations and the reviewer's provisional geometry-derived sampling stations.

- **Q7:** Required vertical sample stations are absolute x=0.05, 0.10 and 0.20 m. Apply these to all cases and record actual line endpoints. Earlier coordinate-derived station suggestions in this register are historical diagnostics and are no longer the acceptance criterion. Exclude intervals within the actual solid/foil hole at those fixed stations.
- **Q24:** S–A has no wall-function selection; the assignment wording is an oversight. Verify and report the actual S–A model without inventing a standard-wall-function option.
- **Q23/Q17:** B0 requires calculating fluctuation velocity, not calculating turbulence intensity. Read actual intensity, either by selecting intensity plus length scale or using the actual k–epsilon inlet intensity. Never reverse-infer intensity from an S–A viscosity ratio. Record which actual case and specification supply it.
- **Q4:** Task A screenshots are allowed; for the remaining tasks use the demonstrated export method, not interface screenshots as result figures.
- **Q19:** "Convergence rate" means iteration count; record this for all five comparison cases, with convergence/terminal status so a capped run is not mislabelled converged.
- **Q13:** If enhanced RSM does not fully converge, report observed behavior and its significance honestly; preserve the run and its original histories.
- **Q16:** Standard initialization is permitted when hybrid initialization fails to converge; record the actual choice and failure/restart history.
- **Q3:** Retain the initial enhanced RSM attempt, then run enhanced k–epsilon; the Part C Case 4 comparison uses enhanced k–epsilon only.
- The authorized student inlet speed remains **50.9 m/s**. Values appearing in other students' questions are not input authority for this case.

## Actual Task A baseline mesh review

Sources: `solver/taskA/taskA_baseline.msh`, `meshing_execution.txt`, `configure_mesh.py`, and actual Fluent import/check output `solver/case01/logs/setup.transcript`. Independent binary parsing is reproducible in `review/verify_baseline_mesh.py`, with full numerical audit in `review/baseline_mesh_audit.json`.

The native mesh is 254,074 bytes, SHA-256 `9f1acf4d40a4f1cf3f203403db57427eebce629bae9e8558298b5eae7e633158`.

**Mesh construction and import accepted:**

- The actual Mesher script/log sets CFD/Fluent preferences, nominal 10 mm global sizing, AllTriAllTet on the actual 2D fluid surface, growth 1.05, and 2 mm sizing/growth 1.05 only on the three named aerofoil edges.
- Independent native binary parsing and Fluent import agree: 4,042 nodes, 7,713 triangle cells, 11,755 faces; dimensions x=-0.5 to +0.5 m, y=-0.075 to +0.075 m.
- Each cell has exactly three incident faces and three distinct vertices; all cell areas are positive. All 7,713 fluid cells are connected through interior faces. Boundary connectivity forms two closed loops (103 and 268 vertices), every boundary vertex has degree two, and Euler node-minus-face-plus-cell count is zero, consistent with one hole. The tested foil-interior point is not inside any fluid triangle.
- All seven named boundary zones persist through native mesh export and actual Fluent import. Foil suction/pressure have 51 line faces each, the finite trailing edge has one, inlet/outlet each have 15, and duct walls have 122/116. Foil-surface line lengths are about 1.922–1.9995 mm and inlet/outlet segments are 10 mm. These are nominal sizing controls; actual interior mesh edges are not all exactly 10 mm.
- Independent cell area minimum 1.452007936e-7 square metres and total 0.1491790490 square metres agree with Fluent's minimum/total "volume" outputs for this 2D unit-depth convention. The measured mesh area is distinct from the CAD kernel area and the analytic curved-boundary area; the mesh has straight boundary segments.
- Fluent `/mesh/check` reports the correct extents and completes without a mesh error. Actual minimum orthogonal quality is 0.258347 and maximum aspect ratio 10.7671, both at the reported trailing-edge-region cell near (0.0994266,-0.0138324) m. These are actual Fluent metrics, unlike the audit's separately defined triangle mean-ratio/equiangle skew measures.
- The actual Fluent zone list assigns `sys_fluid` to air, aerofoil/duct zones to walls, inlet to velocity-inlet and outlet to pressure-outlet. This verifies zone types and fluid designation; it does not read material constants or actual boundary values.

**Disposition:** baseline mesh construction, topology and successful Fluent import/check gates pass for proceeding with Case 1. No assertion of suitable solved y-plus, mesh independence or physical accuracy follows. Task A's final presentation gate remains open until the actual geometry image and mesh image with local inset/labels are visually reviewed. The reviewer did not operate Fluent or Workbench.

## Independent experimental-reference cross-check

Visually inspected actual primary-report renders retained by the data agent: `data/literature/sheldahl_pdf_page_81.png` (printed page 78, Figure 4 lift), `sheldahl_pdf_page_91.png` (printed page 88, Figure 14 drag), and pages 12/13 (printed 9/10, models and facility). Original PDF provenance and render hashes are in `data/literature/source_manifest.json`.

The data agent's preliminary manual 8-degree readings are consistent with independent visual inspection: lift approximately 0.86–0.88 for Figure 4's Re=0.36e6 series and 0.89–0.91 for Re=0.70e6; drag approximately 0.017, 0.015, and 0.016–0.017 for the Figure 14 Re=0.36e6, 0.50e6 and 0.70e6 series. Allowances of about +/-0.03 lift and +/-0.001 drag reasonably describe these manual readings' limited scan/branch/interpolation precision; they are not statistical confidence intervals. No more precise experimental ordinate is approved.

The actual coursework reference plot and its specific series still need recovery. These observations therefore do not authorize silently replacing the brief's curve or computing final model errors. The old report's 0.81 lift reading is not established by this primary figure reading. Original model/facility pages verify approximately 0.1524 m chord, 0.91 m span, end plates and two-dimensional test-section inserts with 2.13 m height. Treating this as an unrestricted finite wing with free wingtip vortices merely because span/chord is near six would misdescribe the actual apparatus. The report discusses nominal Reynolds numbers/turbulence corrections; retain the chosen figure legend and distinguish it from nominal/effective Reynolds definitions rather than silently converting.

## Current review status updates

- Actual FAQ image has now been independently visually inspected; earlier transcribed clarifications are confirmed.
- Actual source PDF/Word/marking workbook have arrived and were read. `review/original_source_review.md` supersedes earlier source-availability uncertainty. The actual specified brief curve supports approximate 8-degree CL=0.81, CD=0.017 for black-filled-circle Sheldahl Re=3.6e5 NACA0012–2D. Keep this distinct from the original Sandia cross-check. AI appendix field template and page-accounting ambiguity remain unresolved in the supplied nine-page brief.
- Task A final presentation is now accepted: `data/taskA/figure1_native_compact.png` and `figure2_mesh_compact.png` were independently viewed. They show the actual native geometry with dimensions/incidence and the actual native-mesh connectivity with a readable local inset/all seven boundary names. Combined with kernel geometry and actual Fluent mesh checks, **Task A evidence/presentation gate passes**. Final placement/legibility in the eventual Overleaf PDF still requires rendering review.
- Case 1 actual setup, numerical controls, initialization and initial residual stopping event are reviewed in `review/case01_setup_review.md`. Native final export content and monitor statistics are retained in `review/case01_raw_audit.json`; plotted-output review is pending.
- Case 1 plotted-output review has now passed, including the true mid-profile solid gap and revised integer ticks. Native pressure/viscous/total force reports also match the independent monitor normalization. **Case 1 complete evidence workflow passes**; solver was explicitly authorized to continue Case 2 without waiting for user/main-agent input. This does not establish spatial convergence or experimental agreement. Detailed disposition and limitations are in `review/case01_setup_review.md`.
- **Case 2 workflow review passes**, residual stopping at 258 with actual standard k–epsilon/standard wall functions, preserved physical inputs and independent result/plot exports. Terminal last-25 force ranges remain 0.1234 percent drag/0.2523 percent lift, so report nonzero iteration drift. Details in `review/case02_review.md`. Actual inherited wall-menu labels close the earlier stationary/no-slip code-mapping uncertainty.

## Final comparison revision after geometric alignment finding

Earlier Case 1/2 workflow passes and the original Case 3 review apply to **retained prealignment evidence**, not final-report data. Native provided-mesh side-zone endpoints identify the common LE node 20633 (not the minimum-x vertex) at (0.00048367698354395,0.00691690311771526) m. Its chord vector matches the original baseline exactly. Inverse-rotated provided boundary coordinates match NACA0012 to maximum approximately 1.1e-9 m, confirming a pure placement shift; the corresponding implied rotation pivot is x=0.0497 m, not assumed exactly 0.05 m. Actual geometry fitting and hashes are in `enhanced_naca_profile_fit_audit.json`.

Main agent has authorized and solver has generated a separate translated `solver/aligned_taskA` and will independently rerun Cases 1–3 under `_aligned`. The new actual CAD inputs are the original plus the exact shift to roundoff, share the provided LE/TE placement and retain the outer duct unchanged. New kernel checks confirm one fluid face, seven edges, two loops, fluid test point true and translated foil interior false. New native mesh contains 7,687 triangles, 4,029 nodes and 11,716 faces, with full connectivity, two closed boundary loops, correct seven zones and positive cells. Actual Fluent check passes; new minimum orthogonal quality is **0.185556** and maximum aspect ratio **15.9404**, at the TE region. These replace the old baseline's metrics for the final Task A report. `aligned_geometry_audit.json` and `aligned_mesh_audit.json` preserve the independent evidence.

**New aligned CAD/mesh gate passes; Case 1 aligned solve was explicitly released.** New figures and solved fields must come from the aligned sources; do not translate old solved plots or mix old forces into the final five-case table. Additional S–A mesh and k–epsilon inlet-length studies must also use aligned geometry so their intended one-factor contrasts remain interpretable.

Early enhanced Case 4 passed its default 1e-3 residual stop but had materially drifting drag. Main agent therefore requires independently saved stricter verification, followed by a newly seeded verified Case 5; see `enhanced_runs_review.md`. The analyst's verification goal is active residuals <=1e-5 and both force ranges/absolute means <=0.1 percent over 100 consecutive updated iterations. Retain original first-threshold evidence and all earlier seed versions.


## Final aligned presentation and Case 2 qualified disposition

Aligned Task A compact native CAD and true-mesh images were independently viewed after source replacement: source mesh SHA256 614e5eee90b0cadab2ba590711e98d79e9f02555f64c6881780ad099e02293be, 7687 triangles/4029 nodes/11716 faces. All seven names and local geometry are readable; Task A image gate passes subject to eventual Overleaf PDF placement. Case 1 aligned full-chain acceptance at 489 is recorded in final_quality_status.md and native/raw/field audits. Case 2 aligned source review completed: qualified inclusion accepted, strict residual gate remains false. See case02_aligned_qualified_audit.json and hash-bound case02_aligned_qualified_acceptance.json. No solver settings were altered by review.
