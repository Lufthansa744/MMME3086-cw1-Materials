# Exact-five-cell correction — ACCEPT

Final delivery: `report/native_fluent_2026-11-10-exact-cells/fig05_rsm_yplus.pdf`

SHA256: `55b51ca829d3ca012339edf61e634059bb96eee40fea5eee676aca95c04cbb8f`

The final PDF contains exactly five separate empty red triangle annotations, each projected from the actual native mesh's three vertices. Independently extracting the real PDF drawing paths identifies cells7588,7316,69,7251 and2573, with no false positives and no false negatives. Maximum vertex discrepancy is0.0000339pt from PDF numeric rounding. Cell6134 between the first selected cell and the last four is not outlined, and neither is cell7578. The five count is correct and the isolated-plus-four topology is now explicit.

The native scientific RGB images are unchanged pixel for pixel. Scalar range, physical box165.1×66.04mm, equal scale, centring and actual axis-tick text/positions are preserved. The old broad bracket and floating “5 cells” label are removed. The0.35pt red outlines are post-export annotations, not native red contour colouring. Independent300dpi rendering of the final delivered PDF exactly matches its reviewed preview. Five outlines are readable with no observed annotation/text collision or clipping.

Figures2,4 and6, including their600dpi and300dpi PNGs, remain byte-identical to the centered accepted set. No Fluent operation, iteration, initialization, mesh movement or physical-data alteration was performed for this correction.

The earlier bracket visual gate was insufficient: a global x-projection of the selected cells also covered other triangles. That annotation acceptance is withdrawn and superseded; the original CFD numbers remain valid. See `SOURCE_FINDING.md` for the explicit correction and `exact_five_cells.json` for raw values, full vertices, centroids and source hashes. Full-report pagination remains subject to actual Overleaf compilation.
