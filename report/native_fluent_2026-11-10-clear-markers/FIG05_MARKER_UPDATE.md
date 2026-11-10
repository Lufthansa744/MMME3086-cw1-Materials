# Figure 5: prominent numbered identification markers

This is the current Figure 5 artwork. It replaces the visually weak thin-outline version without changing the selected cells, scientific image or physical layout. The earlier exact-cell identification remained correct; this update improves visibility at the actual report size.

Five filled red callout circles, each 2.8 mm in diameter, contain white 7.5-point numbers. Five separate 0.65-point leaders point to the actual geometric centres of the five selected triangles. The circles sit above the coloured wall-cell layer, leaving its scalar colours visible. The earlier thin red triangle outlines are removed. The footer reads `Numbered markers: five cells with y+ < 30`.

| Callout | Actual cell ID | Original y-plus |
| --- | ---: | ---: |
| 1 | 7588 | 23.96556544 |
| 2 | 7316 | 25.93608120 |
| 3 | 69 | 19.56839664 |
| 4 | 7251 | 21.53721692 |
| 5 | 2573 | 22.27944689 |

Callout numbers are annotation labels, not native cell IDs. The selected cells are still one isolated cell followed by four consecutive cells. Intervening cell 6134 has y-plus 32.77977224 and remains unmarked. The earlier ambiguous range bracket must not be reintroduced.

## Native source and appearance

The complete scientific base image remains the actual Fluent Save Picture PNG at `solver/native_figures_2026-11-10-centered/case03/yplus_native_context_centered.png`. It is embedded losslessly with unchanged RGB pixels, native scalar fills, mesh context and foil outline. Circles, white digits, leaders, arrowheads, axes and explanatory text are post-export annotations; they are not claimed to be native Fluent field graphics. The source image remains separately preserved.

Figure 5 retains its 165.1 x 66.04-mm artwork box, centred viewport, original palette and range, and the existing 170.94, 19.57 and 40.29 value labels. Visibility was assessed on the full 165.1-mm-wide artwork, including a 96-dpi equivalent-size preview, as well as the detailed 300-dpi render. The markers must be legible without relying on an enlarged crop. Independent checks also verify five correct leader targets, zero false selections or omissions, no crossing leaders and no observed text collisions or clipping.

## Mac patch

Replace the currently active `fig05_rsm_yplus.pdf` in the existing Overleaf project with this directory's PDF, preserving its figure label and dimensions. The matching 600-dpi PNG is supplied if the actual active include uses PNG. Check the include path and extension to prevent an older same-name image from shadowing the replacement.

If the caption says `red outlines` or `bracket`, replace that identification wording with: `Markers 1-5 identify the five suction-side cells with y+ below 30 (post-export annotations).` Preserve all existing numerical values and physical interpretation. Do not describe the selected cells as five consecutive wall triangles.

Figures 2, 4 and 6 in this directory are byte-for-byte copies of the accepted preceding set. No new change to those figures is needed in a report that already uses them. The folder is a complete current four-figure artwork bundle; historical folders remain preserved for traceability.

Use `MAC_PATCH_PROMPT.txt` for the copy-ready instruction, `delivery_manifest.json` for final file hashes, and `review/fig05_clear_markers_2026-11-10/final_acceptance.json` for independent acceptance. Compile and check the integrated report only in the existing approved Overleaf project. No Fluent launch, solution iteration, original data edit or physical-setting change is required for this annotation update.
