# Traceable CFD data processing

`process_forces.py` reads a CSV force monitor and verified metadata, writes a new coefficient CSV and an audit JSON, and leaves the input files unchanged. It uses only the Python standard library. Actual solver exports and derived results are now present in the per-dataset directories.

Required CSV header: `iteration,Fx_N,Fy_N,Fz_N`. Forces must be the total fluid force on the selected body, in newtons and in the same Cartesian frame as the metadata direction vectors. For a two-dimensional model, the solver must first verify the force depth convention and reference area; the script does not infer unit span. Preserve the native Fluent export, and record the conversion from native columns to this CSV in the metadata.

Required metadata JSON keys:

* `case_id`: unique case label
* `density_kg_m3`, `reference_speed_m_s`, `reference_area_m2`: positive numbers read from the actual case/reference settings
* `drag_direction`, `lift_direction`: mutually perpendicular unit vectors, each containing three numbers
* `force_definition`: description of body zones, total pressure plus viscous force, signs, frame and two-dimensional depth if applicable
* `evidence`: object mapping each of the six parameter/definition names above to an object with `path` (an actual local evidence file) and `locator` (line, setting, table or exported field identifying the value)
* `evidence.native_force_source`: mandatory file evidence for the preserved original Fluent force export, with `path` and `locator`; its SHA256 is included in the audit
* `conversion`: mandatory object with `mode` (`identity` or `script`) and `column_mapping`; the mapping must cover `iteration`, `Fx_N`, `Fy_N` and `Fz_N`, each with nonempty `source`, `expression`, `source_units` and `target_units` strings. Expressions must explicitly record the signed conversion or sum of native force columns. Target units must be `iteration` for the iteration column and `N` for forces

An `identity` conversion is allowed only when the input CSV and native source are byte-identical, source column names and expressions equal the target names, and units are unchanged. For example, the `Fx_N` entry is `{"source":"Fx_N","expression":"Fx_N","source_units":"N","target_units":"N"}`. If a source is reformatted, columns are renamed, units/signs change, a 2D force component is explicitly inserted, or multiple native components are summed, use `script` mode and also supply mandatory `evidence.conversion_script` (`path` and `locator`) identifying the actual saved transformation script. The native file must remain separate from the converted CSV. The audit hashes the native file, transformation script, column mapping metadata and the normalized input.

The speed must equal the authorised 50.9 m/s. Other properties have no defaults. Evidence existence, transformation declarations and file hashes are checked mechanically. Agreement of parameters with evidence and correctness of the declared conversion script/column mapping require independent review; the processor does not rerun an arbitrary conversion script or prove that its native input was exported from Fluent.

Run from the workspace, replacing paths with real input files:

```powershell
python data/process_forces.py --forces path/to/forces.csv --metadata path/to/metadata.json --output data/Case1
```

The coefficient definition is the projection of total force along the specified direction, divided by `0.5*density*reference_speed**2*reference_area`. The output records every monitor sample rather than treating the last value as a converged result. A last-window mean, range and linear trend are diagnostics only; residual, mass balance, force stability and flow physics must be reviewed separately before a report value is accepted. Input hashes, source row numbers, output hashes and the script hash provide provenance.

`force_coefficients.svg` plots the measured coefficient history using standard-library SVG generation. This is generated only when real input data are provided. Report-ready PDF/PNG figures and field/profile plots can be prepared after the real exports and plotting environment are available. No LaTeX compilation is performed here.

The final five-case mapping is controlled by `dataset_registry.json`: aligned baseline Cases 1–3 and independently verified enhanced Cases 4–5. Original unaligned and early-stop cases remain archives. Missing final datasets never fall back to an archived solution. `process_case.py` preserves native exports, settings and logs, records source hashes, parses the actual solved equations, separates continuation seed iterations, and produces `case_summary.json` and `workbook_input.json`.

Numerical acceptance normally requires terminal residuals at the actual criteria of at most 1e-5 and drag/lift range divided by absolute mean at most 0.1% over the last 100 updates. This additional verification target is separate from the coursework's 1e-3 criterion. A dataset that misses the additional target can enter the required comparison only through an explicit independent `review/<dataset>_qualified_acceptance.json`, bound to the native forces and final-settings hashes. It must still meet the original residual threshold and the force-stability gate. Its `numeric_final_acceptance_gate_passed` remains false and `reviewed_with_limitation` is true. Figures, tables and workbook acceptance notes must retain that limitation.

`build_comparison.py` uses each case's own native coordinates and fixed case styling. `build_case_workbook.mjs` creates a traceable Excel workbook using the bundled spreadsheet engine; Summary and Acceptance sheets distinguish solver state, numerical gates and independent qualified acceptance. Formula sensitivity and coefficient/stability reconciliation run before export. `plot_cell_fields.py` colours actual mesh polygons and draws sampled native cell vectors, documenting any arrow normalisation. Geometry/mesh compact figures in `data/taskA` use the final aligned native CAD rendering and actual mesh. The earlier placement is retained in `data/taskA_prealignment`.
