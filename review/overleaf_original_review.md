# Independent review of saved Overleaf source

Reviewed file: `report/overleaf_original/source/main.tex`

SHA-256 at inspection: `39ed083c39618d87adb64db714520328223ce5694ba4d829b48e2e6653c48f62`

No edits or compilation were performed. The retained source is a useful structured starting point but is not presently a complete submission. This conclusion concerns the downloaded source and its assets, not a claim about any newer concurrent Overleaf edits.

## Requirements already retained

The four numbered headings exactly match the recovered Word template:

1. `Task A Geometry [16]` — line 53
2. `Task B Solution and data extraction [34]` — line 70
3. `Task C Analysis [50]` — line 167
4. `Task C Boundary Conditions and Results` — line 238

The AIAA class is retained. The source includes Figure 1–13 mapping with a two-panel Figure 6, Table 1, B0 properties, explicit initial enhanced RSM attempt, and appropriate conceptual distinctions between iterative convergence, physical accuracy and confounded mesh/wall-treatment changes. All five displayed equation environments were checked; none ends in punctuation. No `working draft` or `TODO` occurs in visible body text.

## Actions before accepting any submission PDF

### 1 Resolve absent evidence and numerical fields

All 14 named figure PDF assets are absent from the downloaded source directory. The `evidence` macro (lines 38–41) renders empty framed rectangles when files are absent. `submissionfalse` (line 33) allows missing figures and values to compile without errors. There are 42 `Fill` calls, including the definition of the `NA` shorthand, plus 25 table `NA` uses. These include material properties, boundary conditions, model wall setting, convergence criteria, iterations, forces, y-plus, Reynolds number and coefficients.

Action: populate only from validated case evidence and original exports, upload actual figure assets, then activate the existing submission gate and compile in Overleaf. A clean-looking PDF without the words TODO/working draft does not establish completeness when fields are blank. Check every required Figure 1–13 and all five rows by five models in Table 1 after rendering.

### 2 Keep prior enhanced-mesh observations separate from this Windows baseline

Lines 143, 161 and 163 state specific enhanced-mesh counts (20,574 cells, 21,053 nodes, 41,627 faces), line x coordinates (0.0499971, 0.0995105, 0.1995105 m), and hyphenated zone names (`aerofoil-pressure`, `aerofoil-suction`, `aerofoil-trail`). The source's appendix attributes them to the supplied original mesh. Those values may come from valid prior Mac inspection, but their source filename alone does not demonstrate the extraction in this Windows workspace, and the original enhanced mesh has not yet been imported here.

Action: retain these as prior-source observations in internal provenance only until the actual original mesh, its SHA-256 and the actual inspection output are recovered. Recheck when it reaches Windows. Do not overwrite or relabel these enhanced-mesh values as current baseline values.

The independently reviewed current baseline geometry has underscore names (`aerofoil_pressure`, `aerofoil_suction`, `aerofoil_te`) and derived chord-midpoint/TE/downstream x coordinates 0.0495134034370785, 0.099026806874157, 0.199026806874157 m. Report per-mesh line stations and zone names or use geometric definitions with a retained mapping table. Otherwise the old enhanced-mesh coordinates could quietly sample different chord-relative stations in Cases 1–3. The finite trailing-edge centre is the chosen station reference; describe that definition consistently.

### 3 Replace apparent observations with actual observations

- Line 64 describes an existing mesh and inset. At inspection the Task A mesh and final figure have not been reviewed. Add its actual cell count/quality, method settings, boundary transfer evidence, and a readable local inset when available.
- Lines 109–112 describe convergence assessment, but no measured criteria or histories are supplied. Use actual residual thresholds, a defined force-stability window/criterion and a stated mass-imbalance denominator. Distinguish convergence iteration from an iteration cap or nonconverged terminal state.
- Lines 122–128 and 156 describe plotted vectors, cell values, legends and results that are absent. Complete the requested observed wake behavior, unusual y-plus locations and wall-function interpretation using actual fields.
- Line 143 says the initial enhanced RSM run "provides separate convergence evidence". No such Windows calculation exists yet. Do not use completion language until the run is actually retained. The B3 paragraph must compare the observed initial and relaxed RSM residual behavior, lift and drag within 150 words; its current description mostly explains the intended method.
- Lines 161 and 163 assert extracted profiles, common pressure datum and force contributions. Verify actual export settings, all three foil-wall zones, native force units and 2D depth convention before describing extraction as completed.
- C1/C2/C3 paragraphs are scientifically useful interpretation guidance but give no actual model ordering, ranges, differences or locations. Add concise quantitative comparisons rather than leaving only generic theory, while preserving each word limit.
- C4 has no actual model errors, terminal status or supported ranking. It correctly states that the five-model comparison does not prove mesh independence. The recovered brief expressly calls for a mesh-dependence check; retain a real same-model mesh comparison and its numerical evidence before claiming spatial verification.

### 4 Verify the experimental readings and release-specific documentation

Line 274 fixes the Sheldahl curve at Re=3.6e5 and approximate 8-degree coefficients CL=0.81, CD=0.017. The actual figure/digitization evidence is not contained in this source package. The AI prompt record says the earlier assistance read the brief, but is not a graph-reading record. Action: recover the reference plot and retain its caption, relevant curve identity, reading/digitization method and uncertainty before using these values for model errors. Do not increase displayed precision or treat graph estimates as exact tabulated measurements.

References at lines 288–289 cite Fluent 2026 R1 and 2025 R2, while the actual validated executable is Fluent 2022 R2. These can support general theory if their content applies, but cannot establish that a specific 2022 UI option or default was available. Confirm S–A near-wall treatment and other actual options from this installed release. The S–A source paragraph already leaves its actual option blank; fill it from evidence and accurately explain any difference from the assignment's wording.

The confinement ratios derived from stated chord/height values are arithmetically sound and are correctly described as indicators rather than corrections. The unit-span normalization formula and isotropic RMS formula are sound, provided the actual density, intensity fraction, force depth and area conventions are verified.

### 5 Update the AI disclosure and establish the page limit in Overleaf

The appendix (lines 298–304) covers only 5–6 November and Safari/Overleaf report preparation. The present 7 November work includes Windows software verification, native journal scripting, four-agent coordination, actual geometry creation, data processor authoring and independent audits. These activities must be reflected in a factual log before submission. Retain the original historical prompt record and append the current verbatim request and work records rather than rewriting history. Do not label current tool-supported geometry/data/solver assistance as presentation support alone.

The seven-field log and the generic four-row AI guidance table are present, but the actual assessment's seven-point AI template and full guidance appendix are not in the recovered source evidence. Verify their prescribed field labels/content from the original brief. The user-provided approval for drafting and AIAA formatting remains controlling; there is no need to reopen that approved choice.

There are seven explicit `clearpage` commands, so the source intends eight page groups, with bibliography, AI log, guidance table and provenance in the final group. Explicit breaks do not prove the final PDF is eight pages: inserted figures, expanded observations and the appendix can spill. The recovered brief states an eight-page report and an AI-log appendix of at most two pages, but the retrieved excerpt does not establish whether those appendix pages are additional to the eight. Action: verify the exact page-accounting rule from the original assessment and inspect the compiled Overleaf PDF's actual page count, appendix length, overflows and legibility after all evidence is inserted. Do not shrink the approved type or captions merely to hide excess pages.

## Current disposition

Template/heading preservation and displayed-equation punctuation pass source review. Submission completeness, numerical evidence, original enhanced-mesh provenance, experimental readings, current AI disclosure and final page-limit compliance remain open. No solver result or final PDF is approved by this review.

## Subsequent evidence and FAQ corrections

The original enhanced mesh has now been retained in `inputs/` and independently parsed. Its byte count/hash match `inputs/provenance.json`; its actual header verifies all three old-report counts (20,574 cells, 21,053 nodes, 41,627 faces) and the actual wall names `aerofoil-pressure`, `aerofoil-suction`, `aerofoil-trail`. The count/name portion of action 2 is therefore closed. The retained original file and `review/enhanced_header_audit.json` now provide Windows-local provenance. This does not establish numerical settings or a solved enhanced case.

The user's FAQ screenshot, as transcribed and confirmed by the main agent, supplies more specific authority:

- Replace line 161's approximate enhanced-mesh x coordinates with fixed absolute x=0.05, 0.10 and 0.20 m for **all** cases (Q7). Do not substitute the coordinate-derived baseline chord stations suggested in the earlier review; that provisional advice is superseded. Retain actual line endpoints and exclude solid intervals.
- Amend line 109's S–A qualification using FAQ Q24: the assignment's requested wall-function selection is an acknowledged oversight; no S–A wall-function selector is required. Still report the actual installed model settings, rather than claiming the v261 documentation proves v222 UI behavior.
- The B0 table and RMS equation must take intensity from an actual case inlet setting. Q17 does not ask to calculate intensity, only fluctuation velocity; Q23 permits intensity-plus-length-scale specification or actual k–epsilon intensity. Never derive intensity from S–A viscosity ratio, and make the source case/specification clear if they differ.
- B3's requested "convergence rate" should be reported as iteration count for all five cases (Q19); record nonconverged enhanced RSM behavior and significance rather than forcing a convergence claim (Q13). Preserve initialization changes, with standard initialization permitted if hybrid initialization fails (Q16).
- Figure sourcing: Task A screenshots are allowed, while the other tasks should use the demonstrated data/graphics export method (Q4).
- The initial enhanced RSM run remains separate evidence; Case 4 in Part C is enhanced k–epsilon (Q3). Existing intended case mapping is consistent with this clarification.

The screenshot had not yet appeared at its intended local path when this addendum was written; these FAQ points are attributed to the main agent's confirmed user-source transcription pending direct image inspection. Inlet speed remains 50.9 m/s.

The main agent's prepared Task A geometry-method paragraph was reviewed separately. The evidence supports SpaceClaim V22 construction, actual coordinates, finite trailing-edge connector, clockwise coordinate rotation, seven saved named selections and kernel two-loop/point checks. The initial prepared wording "subtracted" implied a Boolean operation not used in the script; the main agent reports correcting this to describe the actual inner-boundary construction. Original Overleaf source remains retained and unmodified.

## Later closures relevant to updating the prepared report

- FAQ has now been independently read from the actual saved image, not just its transcription.
- Task A actual native compact geometry and native-mesh figure/inset were independently visually approved. The mesh has 7,713 triangles and measured Fluent minimum orthogonal quality 0.258347. Use nominal 10 mm global sizing language rather than asserting all interior edges have that length.
- Original brief/Word/marking are now locally retained. The actual page-8 black filled circles confirm the previously proposed CL approximately 0.81 and CD approximately 0.017 at 8 degrees, identified as Sheldahl Re=3.6e5 NACA0012–2D. The graph-reading source concern is closed for those approximate values; retain manual-reading allowances and distinguish the original Sandia cross-check.
- Case 1 actual B0 inputs are now established: density 1.225 kg/m³, viscosity 1.7894e-5 Pa s, speed 50.9 m/s, intensity 5 percent and retained length scale 1 m. Derived Re approximately 3.485e5, one-component RMS 2.545 m/s, qS=158.6871125 N. See the dedicated setup and native-output audits for evidence.
- Actual Case 1 numerical description must say momentum second-order upwind, pressure second order, **modified viscosity first-order upwind**, least-squares cell-based gradients, SIMPLE, hybrid initialization. A blanket second-order statement would be false. Actual URFs are pressure 0.3, momentum 0.7, modified viscosity 0.8 and density 1; operating pressure 101325 Pa.
- Actual residual automatic stop is iteration 324 with all four criteria below 1e-3. Final force D=12.997792729 N, L=141.368577932 N, CD=0.081908307, CL=0.890863635. The actual normalized mass imbalance is approximately 0.000016136 percent, using inlet mass flow as denominator. Do not confuse fraction and percent.
- Source availability still does not resolve the missing official AI-log seven-point template/Appendix 1 or the explicit appendix-in-eight-page rule. See `review/original_source_review.md`.

These closures do not turn the retained original Overleaf source into a completed report; they identify supported replacements for the prepared version. No unavailable result, figure or compiled page count is approved by implication.
