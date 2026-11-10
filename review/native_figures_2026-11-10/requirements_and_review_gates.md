# Independent native Figures 4-6 gates

Scope: read-only review of authentic Fluent postprocessing from retained final solutions; write only within this review directory. No Fluent/Workbench operation, new iteration, solution modification or local TeX compilation by review.

## Actual source requirements

The original brief, B2, asks Figure 4 to show Case 3 velocity vectors around the aerofoil with the wake clearly visible. Its caption must describe the flow pattern and report lift/drag, iteration count and convergence criterion. Figure 5 must show y-plus values on cells touching the aerofoil, including a colour legend and explanations of unusual regions with reference to the actual wall function. B3 asks Figure 6 to contain both velocity vectors and y-plus graphics for the final RSM enhanced-wall case, with an interpretation in its caption. The FAQ Q5/Q14 confirms Figure 6 is RSM only; Q4 distinguishes permitted Part A screenshots from the demonstrated method for other parts; Q6/Q9 requests light-mode presentation and captions below figures.

The current user explicitly requests native Fluent versions of Figures 4-6. The Mac chat identifies the postprocessing guide's Save Picture / PNG / White Background workflow and adjustable vector Scale, Skip and Fixed Length; it separately identifies exported-numeric-data plotting as permitted for other figures. The chat transcript is a source locator/record, not a substituted copy of the original lecture page. Native export identity will be verified from actual local logs/files and images, not from a Fluent-like visual style or an earlier AI claim.

## Current attachment is the layout authority

The November 10 attachment PDF was independently parsed and pages 3/4 rendered. Its figures are vector Form XObjects with these actual printed dimensions:

| Figure | Reference page | Width | Height | Structure |
| --- | --- | --- | --- | --- |
| 4 | 3 | 165.1 mm | 65.008125 mm | Main velocity panel plus trailing-edge inset and speed legend |
| 5 | 3 | 165.1 mm | 66.04 mm | Wall-adjacent-cell y-plus panel, legend and non-overlapping explanatory annotations |
| 6 | 4 | 165.1 mm | 143 mm | Stacked velocity/wake and full-foil y-plus panels, with a further equal-scale maximum-y-plus cell inset |

These are read from actual Form BBoxes and page transforms, not inferred from the old Windows source. Figure 6's height is **143 mm**, superseding the earlier approximately 71-mm Windows arrangement. Detailed evidence is in `reference_form_layout.json`, with the rendered reference pages in this directory. The original attachment contains nine pages; this task does not authorize changing unrelated content or claiming a new report page count.

## Native source and scientific gates

1. **Identity and unchanged solution:** actual native journal/transcript must show reading `case03_aligned` and `case05_verified` final Case/Data pairs. Compare source hashes before/after; no iterations or reinitialisation. Inspect actual Save Picture/graphics export commands and resulting native pictures. External scientific-field painting is not accepted as a native export.
2. **Real vector field:** check signed u/v and speed against original retained domain samples, selected field, displayed range, cell/node setting, Skip, Scale and Fixed Length. Distinguish native display density from a new numerical solution. A fixed-length inset may show direction, but it must not be described as magnitude-proportional. Keep wake coverage and equal geometric scale.
3. **Actual foil-adjacent cells:** y-plus must use cell values with node interpolation disabled for the requested cellwise depiction, and a display scope that actually isolates the foil-neighbour cells. Case 3 has 103 distinct foil-adjacent cells; Case 5 has 413. Positive-y-plus thresholding alone is invalid: saved full domains have 341/913 positive cells, including 238/500 cells not adjacent to the foil. A native register is one acceptable method; a documented native value-range/viewport method is also acceptable if it demonstrably excludes zero-valued interior and remote duct-wall cells while retaining the exact visible 103/413 foil cells. A wall-face-only coloured curve is not the requested cell-contour depiction.
4. **Numerical controls:** Case 3 expected foil-cell y-plus range is 19.56839664-170.9392049; Case 5 is 0.1472955989-6.585910008. Preserve physical maximum-cell inset geometry instead of exaggerating layer thickness. Original signed velocity, speed and pressure ranges, exact foil-neighbour IDs and minimum/maximum controls are in `expected_native_field_controls.json`.
5. **Layout-only composition:** data may crop/assemble authentic native panels and add factual annotations outside scientific layers. Cropping/placement must use uniform scales or documented physical axis transforms; do not distort cells/aerofoil, recolour/repaint field values or silently replace native legends with a mismatched range. Panel arrangements and printed boxes must match this attachment.
6. **Readable and collision-free:** independently inspect final native exports and composed figures at actual print size; verify colour legends/units, arrow visibility, markers, all axes and annotation endpoints. Require no label/leader overlap, no cropped glyphs, no inset-geometry distortion and no misleading caption. The raw native pictures must remain separately retained.

## Disposition

Pending actual native files and final layout. Hashes alone cannot close these gates. Final acceptance requires actual native settings/logs, native image inspection, field/cell checks and composed-figure comparison with the current reference PDF.
