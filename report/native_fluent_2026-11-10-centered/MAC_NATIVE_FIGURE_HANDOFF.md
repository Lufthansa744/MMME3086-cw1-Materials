# Centred native artwork: Mac integration

This set supersedes the earlier `report/native_fluent_2026-11-10/` artwork set for the current Mac report. Use the four files together and verify their final hashes against this set's independent acceptance record. The full copy-ready Mac instruction is `MAC_FINAL_PROMPT.txt`.

## What changed

| Figure | Change | Actual display window |
| --- | --- | --- |
| 2 | Retained byte-for-byte from the accepted native version | Full duct and local mesh views unchanged |
| 4 | Retained byte-for-byte from the accepted native version | Baseline RSM velocity and trailing-edge inset unchanged |
| 5 | New native export with vertically centred foil | x = -8 to 108 mm; y = -17.470596534 to 20.529403466 mm |
| 6(a) | New native export with horizontally centred foil and genuine upstream data | x = -70 to 170 mm; y = -30 to 25 mm |
| 6(b)/inset | Original accepted native scientific layers retained | Full wall-cell and equal-scale maximum-cell windows unchanged |

Figure 5's earlier y window was -24 to 14 mm, centred at -5 mm. The actual foil boundary spans -7.125180755 to 10.183987687 mm, with midpoint 1.529403466 mm. The new 38-mm-tall window puts equal space above and below that actual boundary box. This is a camera/axis-window change, not a vertical displacement of the mesh or scalar data.

Figure 6(a)'s earlier x window was -10 to 230 mm, allocating extra space to the downstream wake. The new 240-mm-wide window is centred at x = 50 mm and preserves the same physical magnification, arrow scale and panel size. The actual trailing edge is at approximately 99.510484 mm, so 70.489516 mm, or about 0.705 chord, remains downstream. The brief does not impose the C1 profile locations on this vector viewport; the separate x = 200-mm profile is unaffected. The new upstream field is exported by Fluent from the same saved solution, not created by padding or shifting the old raster.

## Physical boxes and files

| Figure | PDF | Artwork width x height |
| --- | --- | --- |
| 2 | `fig02_mesh_bc.pdf` | 159.997422 x 73.998808 mm |
| 4 | `fig04_rsm_vectors.pdf` | 165.1 x 65.008125 mm |
| 5 | `fig05_rsm_yplus.pdf` | 165.1 x 66.04 mm |
| 6 | `fig06_enhanced_combined.pdf` | 165.1 x 143 mm |

PDFs retain native raster scientific layers losslessly, plus vector axes, typography and annotations. They are not all-vector field graphics or unedited screenshots of the whole Fluent window. Same-stem 600-dpi PNGs and 300-dpi print previews are also supplied. Keep explicit file extensions in the active Overleaf includes so older same-name images cannot shadow the selected PDF/PNG.

Figures 2/4 retain their accepted source bytes. Figure 5 still shows all 103 actual foil-adjacent cells with native node values disabled, the same y-plus range and native palette. Figure 6(a) uses native rake sampling, not cell-centred sampling. Its requested/valid/excluded point counts are recorded in the new manifest; the earlier set's 504-fluid-point count does not apply. Figure 6's 413 wall-cell values and thin-layer geometry remain unchanged, with colours resolved honestly in the equal-scale inset.

## Integration and numerical scope

Use the current Mac Overleaf source, not the historical Windows source ZIP. Verify the active main file and include chain before replacing artwork. Retain the approved AIAA template, prescribed sections, figure labels, current body and verified numerical conclusions. Figure 1's verified SpaceClaim pixels and Figures 3/7-13 remain. `figure6_caption.tex` supplies the minimal native rake/near-wake wording and actual thin-cell display explanation; retain the existing Figure 6 label when applying it.

No solution iterations, initialisation, geometry movement or physical-setting edits are required by this display change. The final source Case/Data hashes and executed native export log are retained under `solver/native_figures_2026-11-10-centered/`. New composition and independent-centering/native-source audits are under the matching `data/` and `review/` directories. This work does not remove the earlier strict-continuity or mesh-sensitivity qualifications.

Compile and inspect the integrated report only in the existing approved Overleaf project. Standalone artwork acceptance does not certify the updated full report's final page breaks, captions or page count. Review the AI log for an accurate account of the tools and assistance actually used.
