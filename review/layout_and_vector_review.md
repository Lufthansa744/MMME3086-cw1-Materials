# Independent layout and vector-asset review

No report TeX was compiled locally. The final PDF, its page count and its actual line/page breaks remain unaccepted until an allowed Overleaf compilation is inspected.

## Source layout

The approved `new-aiaa.cls` supplies 10 pt Times-style text, US letter paper and 1-inch margins: a 165.1 by 228.6 mm text area. The source's repeated package loads introduce no conflicting options. The class already provides `titlesec`, so the main file's section-spacing commands have a provider. The four section headings, table/minipage structures and equation environments have no obvious structural error. The final coefficient table's six columns and supplied width have no evident intrinsic-width conflict; exact font metrics/overfull warnings still require TeX.

The source formerly imposed seven artificial page breaks. Combined with indivisible `[H]` figure/caption boxes and long bold captions, these could push a block onto a fresh page and then immediately waste the remaining page after the following forced break. Pages labelled 1, 5 and 7 were particularly dense by static height estimates. Removing these seven `clearpage` commands is the smallest appropriate structural correction; it preserves sections, figure order, actual type sizes, image sizes and class/margins. It does **not** prove an eight-page result. Keeping `[H]` retains the requested figure order and association with its discussion, while natural page breaks can use remaining space.

The table qualification note is correctly changed to a local `footnotesize` group with the paragraph ended inside the group. The previous switch back to normal size before ending the paragraph would have applied the normal paragraph baseline spacing to the small note. The current change preserves readable small text without that unnecessary vertical spacing. If the final rendered note becomes detached from its table, its placement should be reviewed there; static source alone does not establish an orphan.

The current diagram and graph sizes should be retained. Exact source-derived print boxes and inherited SVG font sizes are in `static_print_box_audit.json`. Figure 1 actually prints at 144.906 by 48 mm because its height limit controls; Figure 2 is 165.1 by 76.359 mm. Other full-width figures use 165.1 mm; the four half-width figures use 80.0735 mm. Minimum base label sizes are approximately 7.75-8.22 pt, with appropriate smaller mathematical superscripts. Original PNG effective resolution is 492-561 ppi. No additional reduction is recommended merely to force a speculative page count. Source SVG dimensions, rather than twice-resolution PNG dimensions, must determine label-font conversion.

## Scientific vector PDFs

The final eleven PDFs in `data/print_assets`, Figures 3-13, pass independent parsing and source comparison. All displayed source SVG text is extractable and matches character-for-character after whitespace normalization. Arial TrueType is embedded; Figure 6 additionally embeds Segoe UI Symbol for the proportionality symbol, which Arial lacks. There are no raster-image XObjects in the scientific PDFs. CropBox equals MediaBox; each PDF's physical box matches its original report print dimensions, and all extracted character bounds lie inside the page.

An earlier export lost the proportionality glyph and mishandled three-digit hexadecimal colours. Those earlier PDFs are **not** accepted. The corrected exports retain original SVG/PNG data assets unchanged and fix the converter/font handling. Current independent hashes and results are in `vector_pdf_independent_audit.json`.

All eleven corrected PDFs were independently rendered with Poppler at their corresponding original PNG pixel dimensions. Average absolute RGB differences against original PNGs are only 0.679-1.639 on a 0-255 scale, consistent with different rasterizers/font rendering rather than altered data or plot geometry. The formerly affected Figure 6 was visually checked after correction: proportionality symbol, colours, true cell zoom, legends and bounds are correct. A half-width pressure figure was also visually checked. Original source sampling, scientific layout and scale are retained; the converter does not reinterpolate numerical data. Replacing only the eleven main-file image extensions with these accepted PDFs is approved at the source/asset level.

This review does not authorize bypassing the Overleaf site permission denial. No substitute local report rendering or pretend submission PDF was created. The next required validation is an allowed Overleaf build followed by its page/appendix count, overflow warnings, figure/caption legibility, table-note placement, bibliography and appendix inspection.


## Final packaged source identity

The final main file now references the eleven accepted same-name vector PDFs for Figures 3-13 and original PNGs for Figures 1-2. Final main SHA256: `93391df3f80c4e90e85a5af5c1f13c2fbd26d03f4823f23ecbadc02831a34898`. The approved class remains byte-identical (SHA256 `aead59d4596beda8879a84d074722e16ef3152ee625087d8e25337f1750f759f`). The final source ZIP has 20 unique members, all byte-identical to prepared sources, including all 13 referenced image assets, class/BST, table and provenance files; ZIP SHA256 `527ef3cc1616a087a4b57c23a75a55348ba6d9c5bf577c5c1eb63bb961aaad95`. All eleven PDF hashes match the independently accepted corrected vector exports. No extra stale PNG enters the final ZIP in place of a selected PDF. Four headings, balanced environment nesting, removal of artificial clearpage commands and grouped footnote paragraph are confirmed. See `final_print_package_audit.json`.

Disposition: final source/asset/ZIP consistency PASS. Overleaf compilation, real page and appendix counts, rendered line/page breaks and legibility remain outstanding; no local TeX compilation was used.
