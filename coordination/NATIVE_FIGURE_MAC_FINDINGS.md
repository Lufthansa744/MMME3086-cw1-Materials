# Native graphics continuation: Mac evidence and scope

The relevant visible messages and command outputs from `MMME3086 cw1 (Mac)` were read on 10 November 2026. Hidden reasoning and unrelated conversation were excluded. The course postprocessing text was retrieved from the Mac chat's recorded command output and saved in `mac_postprocessing_practical_extracted.txt`.

The recorded teaching evidence identifies two routes:

- `CFD-PostprocessPractical2026.pdf`, PDF page 4, Step 3: display graphics in Fluent, then File > Save Picture > PNG > White Background. Step 4 explicitly discusses vector Scale, Skip and Fixed Length.
- The same practical, pages 7-8: export solution values as ASCII, sort and plot XY comparisons. `CFD-Lecture2.pdf`, page 40, explicitly permits other software, with spreadsheets as an example.

This task therefore targets native scientific graphics layers for Figures 2, 4, 5 and 6. Figure 1 already contains native SpaceClaim picture pixels; Figures 3 and 7-13 retain their source-data plotting route. No new CFD iterations, boundary conditions, material properties or physical models are authorised or needed for this postprocessing task.

## Layout authority

The user-supplied `MMME3086_CFD_Coursework_2026___Yang_LIU_20617209-4.pdf` is the layout reference. It has nine pages. Mac messages report eight pages of body/references and a separate AI appendix; this task does not alter that report or compile it locally.

Physical artwork boxes independently extracted from that PDF:

| Figure | Width mm | Height mm | Structure |
|---|---:|---:|---|
| 1 | 132.8251 | 43.9983 | Two native CAD image panels; retained |
| 2 | 159.9974 | 73.9988 | Full duct mesh plus local mesh inset, seven boundaries and dimensions |
| 4 | 165.1 | 65.008125 | Main velocity vectors and trailing-edge inset |
| 5 | 165.1 | 66.04 | Whole-cell wall-adjacent y-plus, mesh context and values |
| 6 | 165.1 | 143.0 | Velocity panel; full-foil wall-cell panel; equal-scale maximum-y-plus inset |

The Figure 1 and Figure 2 PDF image pixels were independently matched to the current original PNGs, including the corrected Figure 2 dimension/axis annotations. Figure 6 differs from the earlier November 7 side-by-side Windows layout; that historical layout must not be substituted.

## Data and software identity

Only the saved final `solver/case03_aligned` and `solver/case05_verified` Case/Data pairs supply the scientific fields. The aligned baseline mesh supplies Task A's native mesh views. Raw Fluent Save Picture outputs, native EPS where available, complete startup arguments, display controls and transcripts are preserved separately. The solver agent exclusively controls Fluent; no external plotting program may replace the scientific arrows or cell colour fills in a native-labelled replacement.

Postprocessing may crop and uniformly scale native layers, compose panels and add coordinate axes, leaders and labels. Actual coordinate transforms, native colour limits, palette, sampling and all added annotations require independent checks. Native source images remain preserved. Native rendering does not resolve the already reported convergence/grid-sensitivity limitations.

## Acceptance

The replacement must match the supplied report's physical box and panel structure; preserve orthographic geometry and complete field scope; remain readable at the final printed width; and have no annotation overlap or cropping. Larger vectors must be generated in Fluent, with the selected scale/skip/style recorded. Main arrows remain velocity-scaled; any fixed-length inset is labelled as direction-only.

The Mac chat continues to own the current Overleaf source. New artwork is delivered in an independent native-graphics folder with drop-in filenames and a provenance manifest. This avoids replacing the older Windows report source over the newer Mac document. Compilation remains restricted to the approved Overleaf project.
