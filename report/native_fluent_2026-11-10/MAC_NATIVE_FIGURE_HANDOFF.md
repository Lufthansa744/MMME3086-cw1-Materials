# Native Fluent artwork for the current Mac report

Use this addendum before the historical Windows source-package instructions. The current Mac Overleaf document has already evolved from the older Windows `report/prepared/main.tex`. Preserve that Mac document, its approved AIAA class, sections, captions and AI appendix. Do not upload the historical source ZIP over it.

## Assets and exact printed boxes

The layout authority is the user-supplied nine-page `MMME3086_CFD_Coursework_2026___Yang_LIU_20617209-4.pdf`.

| Figure | Replacement | Artwork width x height | Scope |
| --- | --- | --- | --- |
| 1 | Retain existing asset | 132.8251 x 43.9983 mm | Existing SpaceClaim picture pixels independently matched to the native source |
| 2 | `fig02_mesh_bc.png` or `fig02_mesh_bc.pdf` | 159.9974 x 73.9988 mm | Native full-duct and local mesh, seven boundary labels and dimensions |
| 4 | `fig04_rsm_vectors.pdf` | 165.1 x 65.008125 mm | Native Case 3 cell-centred velocity vectors and native fixed-length direction inset |
| 5 | `fig05_rsm_yplus.pdf` | 165.1 x 66.04 mm | Native flat cell-colour contours of the 103 foil-adjacent cells, native mesh context |
| 6 | `fig06_enhanced_combined.pdf` | 165.1 x 143 mm | Native enhanced-RSM vectors, all 413 foil-adjacent cells and equal-scale maximum-cell inset |

Figure 6 uses the three vertically stacked panels of the current Mac PDF. The older Windows approximately 71-mm-tall Figure 6 is not the layout authority. Figures 3 and 7-13 remain unchanged.

## Origin of the graphics

The mesh, arrows, cell colour fills and foil outlines in the replacements are Fluent-rendered Save Picture output from Ansys Fluent 2022 R2. Native PNGs are embedded without recolouring, sharpening, external field reconstruction or non-uniform geometry scaling. Coordinate axes, panel headings, boundary/dimension labels, numeric legend labels and explanatory leaders/brackets are added during composition. Native colour-bar strips are preserved from the native palette donors.

The deliverable PDFs therefore contain losslessly embedded native raster scientific layers and vector typography/annotations. They are not all-vector field graphics and are not unmodified whole-window screenshots. Raw PNG/EPS pictures and provenance remain under `solver/native_figures_2026-11-10/`. An EPS container does not imply that its scientific image is vector rather than raster.

Case 3's main vector panel retains actual cell-centred samples with native Skip 3. Its trailing-edge inset uses fixed-length arrows to show direction and must retain the direction-only description. Figure 6(a) uses velocity-proportional arrows evaluated and drawn by Fluent on regular rake surfaces. Its dense sampling has 12 rakes with 45 requested positions each: 540 requested positions, 36 inside the solid excluded, and 504 actual fluid samples. Native interpolation and sampling affect presentation, not the saved numerical solution. Do not describe that panel as cell-centred.

The enhanced mesh's wall cells are physically very thin in the full-foil view. A native black foil outline provides geometric context; the equal-scale inset resolves actual cell thickness and colour without artificial inflation. The pure native full-field image is retained separately for inspection.

## Minimal Mac update

1. Pull the published repository main branch and read the final acceptance record alongside the artwork manifest in this folder.
2. In the existing approved Overleaf project, replace the active artwork assets only. The Mac chat identifies the current source as `nov09_v3/report.tex`; verify its actual `includegraphics` paths before uploading. Keep explicit PDF extensions for Figures 4-6. For Figure 2, the supplied PNG supports the existing explicit PNG include, while the PDF is an alternative with the same artwork box.
3. Figure 6's panel heading is changed from the old cell-centred claim to a native rake-sampling description. `figure6_caption.tex` supplies the corresponding caption, preserving the physical claims and numerical values while naming rake sampling and the equal-scale colour inset. Paste that caption over the existing Figure 6 caption, retaining its existing label. Recheck the B3 caption word limit in Overleaf after integration.
4. Retain Figure 5's physical interpretation of the five suction-side cells below y-plus 30. Its red bracket is a factual post-export annotation of their true streamwise interval; it is not a replacement of native scalar fill and must not be called native red cell outlines.
5. Compile only in the existing Overleaf project. Inspect the actual compiled pages for figure size, caption placement, line breaks, page count, unresolved references and overlap. No local TeX compilation was performed for this native-artwork task.
6. Review the AI usage log for factual accuracy after this additional work: this native-export/composition task used Codex with solver, data and review sub-agents. Record the actual tools and assistance as required by the course, retaining any separately used tools and the author's own verified account. This addendum does not rewrite the Mac appendix or assert that earlier tool descriptions are complete.

## Numerical scope and audit

Only saved final Case 3 and Case 5 Case/Data files and the aligned Task A baseline mesh were read. No solution iterations or reinitialisation are part of this task. The native-display work does not change Case 2/3's qualified convergence assessment, demonstrate mesh independence or remove the stated experimental/confinement limitations.

Composition scripts and layer hashes are under `data/native_figures_2026-11-10/`; independent geometric, scalar, sampling, print and source-identity checks are under `review/native_figures_2026-11-10/`. Exact selected native layers and final artwork hashes are recorded in the delivery manifest. Historical diagnostic pictures are retained as evidence and are not selected replacement assets.
