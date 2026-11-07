# Data contract tied to the recovered coursework

Current status: the original brief is now available as `inputs/MMME3086-CFD-V2.0.pdf`; its page-8 reference reading is recorded in `data/literature/brief_reference_reading.json`. Actual solver exports, source-preserving processing and print-sized figures are present per dataset. Final physical dataset selection is exclusively `data/dataset_registry.json`; this original planning map is retained for requirement traceability. Its statements about unavailable original sources below describe the initial discovery stage, not the current status.

Source: `coordination/recovered/task_ABC_recovered.txt` and `word_template_recovered.txt`, recovered by the main agent from a previous chat. These are recovered text, not the original assignment PDF. Numerical settings still require actual solver evidence.

## Case sequence

| Dataset identifier | Mesh and model | Required evidence |
|---|---|---|
| Case1 | Task A mesh; Spalart–Allmaras; specified standard wall treatment; SIMPLE | Actual model settings, residuals, force history, all surface/profile exports |
| Case2 | Duplicate Task A mesh; standard k-epsilon; standard wall functions; SIMPLE | Independent saved setup and results |
| Case3 | Duplicate Task A mesh; RSM; standard wall functions; SIMPLE | Also velocity vectors and wall-adjacent y+ visualization |
| Case4_initial_RSM | Provided enhanced boundary layer mesh; RSM; enhanced wall treatment; SIMPLE | Preserve initial attempt, settings, residuals, terminal status, forces and available exports separately |
| Case4 | Provided enhanced boundary layer mesh; k-epsilon; enhanced wall treatment; SIMPLE | Record restart/initialisation provenance and convergence rate |
| Case5 | Duplicate enhanced setup; return to RSM; Reynolds stress relaxation 0.25, other turbulence and momentum relaxation 0.5 | Record which Case4 solution was inherited, independent settings/results, velocity vectors and y+ visualization |

The initial enhanced RSM attempt is separate from the five comparison cases. The user-supplied FAQ clarifies that the requested standard wall function for S-A was a brief oversight; record Fluent's actual S-A near-wall treatment rather than inventing an unavailable option.

## Required original exports per run

* Native residual history for each solved equation, with exact stopping criteria and iteration numbering including restarts
* Body pressure, viscous and total lift/drag; continuous total force histories preferred; selected zones and positive directions recorded
* Suction-side static pressure and y+, and pressure-side static pressure and y+, with x/y coordinates, zone identifiers, units and pressure reference
* Velocity magnitude across the full duct on the FAQ Q7 prescribed fixed absolute x coordinates 0.05 m, 0.10 m and 0.20 m, each with y from -0.075 m to +0.075 m; save endpoints and sample coordinates. At x=0.05 m retain the separate fluid portions around the aerofoil, with the solid interval explicitly absent. Do not join across it as fluid data
* Actual air density, dynamic viscosity, inlet velocity and turbulence specification, inlet turbulence intensity if actually defined, reference values, 2D depth/force convention, chord and reference area
* Saved case/data, setup, journal/transcript, mesh statistics and quality, and final mass balance

Keep each native export intact. Any normalized CSV is a derived file, with the native source hash and conversion script recorded. Preserve pressure/suction surfaces separately and split at leading/trailing edges explicitly; do not merge duplicate x coordinates before inspecting topology. Do not silently interpolate profiles between cases. Store native coordinates and document any x/c conversion using the actual rotated geometry. The geometric TE has x approximately 0.0990268 m, but this does not override the FAQ Q7 fixed sampling x=0.10 m. Likewise do not replace the prescribed x=0.05 m and 0.20 m with rotated-chord-derived stations.

## Derived quantities

* B0 Reynolds number: `rho*U*c/mu`; rho, mu and c come from actual settings/geometry
* B0 isotropic RMS fluctuation: `U*I`, only when the actual inlet intensity `I` is available and interpreted as `sqrt((u'^2+v'^2+w'^2)/3)/U`; convert percent to fraction before multiplying. FAQ Q17 requests the fluctuation, not an inferred turbulence intensity. FAQ Q23 permits S-A intensity plus length-scale input or the actual k-epsilon inlet intensity for this calculation. Do not infer an intensity from S-A viscosity-ratio input
* C4 normalization: `q=0.5*rho*U**2`, `CD=D/(q*S)`, `CL=L/(q*S)`; coursework planform convention uses 1 m depth and 100 mm chord, so intended `S=0.1 m²`; actual solver force depth and reference settings must be checked before applying it
* Report force values must distinguish a stable converged statistic from a nonconverged terminal or bounded-window statistic

## Figures and report mapping

| Output | Source |
|---|---|
| Figure 1 | Actual Task A geometry, dimensions, 8-degree AoA |
| Figure 2 plus inset | Actual 10 mm triangular duct mesh, 2 mm aerofoil sizing, 1.05 growth; boundary labels; caption under 100 words |
| Figure 3 | Case1 native residual history; criterion, iterations, interpretation |
| Figures 4–5 | Case3 velocity vectors/wake and wall-adjacent y+ with readable range |
| Figure 6 | Case5 enhanced RSM velocity vectors and y+; interpretation within 150 words |
| Figures 7–9 | All five cases, cross-duct velocity magnitude at each of the three defined x stations; each explanation under 100 words |
| Figures 10–11 | Pressure-side and suction-side static pressure, all five cases; each explanation under 100 words |
| Figures 12–13 | Suction-side and pressure-side y+, all five cases; combined explanation under 100 words |
| Table 1 | Each five-case lift, drag, iteration count/status, CD and CL; explicit normalisation provenance |

`process_forces.py` supplies coefficient history and stability diagnostics. It does not declare convergence or generate the coursework residual plot from a force history. Literature comparison needs the actual reference curve at 8 degrees, its Reynolds number and setup; none are digitized or estimated here.

FAQ Q4 accepts screenshots for Part A; remaining plots must use the coursework numerical export method and retained raw values. FAQ Q20 accepts working with the limited literature-figure resolution; state actual reading uncertainty rather than assigning unjustified digits. The experimental-figure investigation is recorded separately under `data/literature` and cannot be substituted for the absent brief reference curve without checking its identity.

## Local discovery outcome

The read-only filename searches covered Documents/ChatGPT, Documents/Codex, Downloads, Desktop and D:/Downloads. No original CFD case/mesh/native result exports were found. The `MMME3086-NM-Coursework-2526 - Template.docx` in Downloads is a separate Numerical Methods coursework. D:/Downloads contains `AIAA template.tex`; the main agent owns template/Overleaf decisions. No CFD numerical result or plot has been created without actual exports.
