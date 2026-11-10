# Figure 5: exact five-cell annotation correction

This set supersedes the earlier Figure 5 bracket annotation. The CFD values and the count of five are unchanged; the previous visual selector was ambiguous and its acceptance is superseded for this annotation.

## Verified selection

The actual suction-side cells with raw y-plus below 30 are:

| Actual cell ID | Raw y-plus |
| --- | ---: |
| 7588 | 23.96556544 |
| 7316 | 25.93608120 |
| 69 | 19.56839664 |
| 7251 | 21.53721692 |
| 2573 | 22.27944689 |

These five cells are not consecutive. Cell 6134, with y-plus 32.77977224, lies between the first selected cell and the following four along the suction wall. The apex of cell 7578, with y-plus 40.23124347, also projects into the old bracket's left end. Seven suction-side triangles therefore overlapped the old bracket's horizontal projection, even though only five satisfy the criterion. The trailing-edge cell 7516 is not one of those seven projected suction-side triangles.

The previous check established that the bracket covered the selected cells, but failed to check that it excluded unrelated cells. This was insufficient. Shrinking a single bracket cannot identify the non-contiguous five-cell subset correctly.

## Correction

The wide bracket and floating `5 cells` label are removed. Five individual thin, closed red triangle outlines now follow the three actual mesh vertices of exactly the five selected cells. The footer reads `Five red-outlined cells: y+ < 30`. The red lines are post-export identification annotations; they are not a new scalar colour field or native Fluent red contours. The original Fluent scientific image, scalar colours, numeric values, actual axes, vertical centring and 165.1 x 66.04-mm artwork box are retained.

The independent check requires both selection completeness and selection exclusivity: five correct polygons, no false-positive polygon and no missed selected cell. It also verifies native-image RGB preservation, exact vertex mapping, print readability and the removal of the ambiguous bracket. See `review/fig05_exact_five_cells_2026-11-10/` for the finding and final acceptance record.

## Mac update

Replace only the active `fig05_rsm_yplus.pdf` in the current approved Overleaf project with this set's corrected PDF. The same-stem PNG is also supplied if the actual active include uses PNG. Verify the path and explicit extension so an older same-name file is not selected.

Figures 2, 4 and 6 in this set are byte-for-byte copies of the accepted centred set, provided only to keep a complete current four-figure bundle. They do not require another change in a Mac report that already uses that centred set. Historical artwork and audit records remain preserved as provenance, with this correction as the current instruction.

If the current Figure 5 caption refers to a bracket, replace only that identification wording with: `The five cells are individually outlined in red (post-export annotations).` Preserve the actual values and physical interpretation. The five cells must not be described as a continuous group of five adjacent triangles.

Use `MAC_PATCH_PROMPT.txt` for a copy-ready instruction. Compile and inspect the integrated report only in the existing Overleaf project. This standalone figure correction does not itself certify the updated report's page breaks or page count. No Fluent solution, original CASE/DATA file, mesh or physical setting is changed for this annotation correction.
