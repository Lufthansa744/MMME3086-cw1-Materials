# Print assets

Figures 3–13 are exported directly from the existing scientific SVGs into the correspondingly named `fig03_*.pdf` through `fig13_*.pdf`. They retain source coordinates, native mesh polygons, sampled curves, colours, line styles, labels, aspect ratios and the original reporting scales. No raw values were recalculated, no raster tracing was used, and no LaTeX was compiled. All original SVG and PNG files remain unchanged.

These PDFs contain vector drawing operators and extractable text, with zero raster image objects. Arial TrueType subsets are embedded; the proportionality glyph in Figure 6 uses an embedded Segoe UI Symbol fallback. Unsupported source SVG vocabulary causes the exporter to stop. The existing source log-tick superscripts use the exporter's explicit 0.35-parent-em baseline rise; independent visual comparison confirms their legibility and layout.

`print_asset_audit.json` records each source SVG/PNG hash, output PDF hash, embedded-font hashes, source drawing counts, PDF operators, physical page size and font sizes. `print_size_audit.csv` covers all 13 figures using the actual AIAA text width of 165.1 mm, the 0.485-width minipages, and both graphic width/height constraints in the prepared report. Existing PNG effective resolution is 492–561 dpi, already sufficient for print. Main text in the figure labels is about 7.75–8.22 pt at the current figure sizes; mathematical superscripts are intentionally smaller. Further shrinking would reduce readability.

The independent review is `review/vector_pdf_independent_audit.json`. All 11 PDF hashes passed complete source-text extraction matching, embedded-font inspection, zero-raster inspection, physical boxes, text bounds, Poppler rendering and comparison with the original PNG. Mean RGB pixel differences were 0.679–1.639 on a 0–255 scale; antialiasing and font rasterisation prevent pixel identity. Original scientific geometry and text are preserved.

Source numerical/CAD lineage remains in these existing records:

- `data/final_data_manifest.json`: final physical dataset registry, raw-processing summaries and report PNG hashes
- `data/taskA/compact_figures_manifest.json`: Figures 1–2 native CAD/mesh sources
- `data/case01_aligned/compact_plot_manifest.json`: Figure 3 residual data and SVG generation
- `data/case03_aligned/cell_field_plot_audit.json`: Figures 4–5 actual mesh/cell-field mapping
- `data/case05_verified/cell_field_plot_audit.json`: Figure 6 actual enhanced mesh/cell-field mapping
- `data/comparison/comparison_audit.json`: Figures 7–13 native profiles/surfaces, dataset hashes and fixed case styles

Use the PDFs at the same aspect ratio and graphic width/height limits as their existing PNG counterparts. Figures 1–2 were audited but are not replaced here. Report integration and Overleaf compilation remain the main agent's responsibility.
