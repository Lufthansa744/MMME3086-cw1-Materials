# Native Ansys CFD deliverable

Final prescribed five-case physical sources: case01_aligned, case02_aligned, case03_aligned, case04_verified, case05_verified. Each folder contains actual settings, native transcript, initialized/continued and final Case/Data pairs, force and mass monitors, raw exports, and a hash-bearing manifest. Formal source selection is deliberate: earlier case01/02/03 folders are retained prealignment diagnostics; case04/case05 are retained early-stop diagnostics.

Task A final geometry/mesh/images: aligned_taskA. The original supplied enhanced mesh is preserved in ../inputs. The aligned baseline uses the independently verified rigid translation recorded in ../review/enhanced_naca_profile_fit_audit.json. Global 10 mm, foil 2 mm and growth 1.05 are retained.

Final Workbench delivery: workbench/final_coursework_cases.wbpj together with its matching _files directory. Native import and real Duplicate operations are logged in final_project_build.log. Every final Case and final Data file was separately imported; final_project_sources.json binds source paths and SHA256. Historical coursework_cases.wbpj is retained and is not the final delivery.

Strict numerical target is an analyst supplement: all active scaled residuals <=1e-5 and both force ranges/absolute means <=0.1% over the final 100 new-model iterations. Formal cases 1,4,5 meet this target. Cases 2 and 3 met the assignment 1e-3 criterion but retained scaled-continuity plateaux above the supplementary target; they are explicitly qualified, not strict passes. Independent acceptance is under ../review. First assignment-threshold crossings and final stopping iterations are distinct.

Supplemental studies are not extra prescribed cases: sa_grid_medium and sa_grid_fine use identical aligned SA physics and independent hybrid initialization on independently generated triangular meshes. sensitivity_ke_length_001 isolates inlet length scale 0.01 m against the formal Case2 value 1 m, holding intensity 5% and all other actual inputs fixed. No grid independence or experimental validation is implied merely by completing these runs.

case02_mass_diagnostic is read-only postprocessing of the saved formal Case2 final state. Native volume-integral reports confirm mass-imbalance field units kg/s; raw cell-id and cell-volume are preserved. It performs no iterations and does not overwrite the formal pair.

All numerical report values must be traced to these raw/native files and the data agent outputs. Actual material values are rho=1.225 kg/m3, mu=1.7894e-5 Pa s; inlet U=50.9 m/s. Formal inlet turbulence selection is intensity 5% and length scale 1 m. This is a recorded input, not a measured tunnel condition.
