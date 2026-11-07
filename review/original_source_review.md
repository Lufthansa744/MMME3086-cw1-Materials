# Review against original assessment files

Original sources now retained: `inputs/MMME3086-CFD-V2.0.pdf`, `MMME3086-CFD-Template-2026.docx`, and `CFD-IndicativeMarkingScheme2026-27.xlsx`; original hashes are in `inputs/source_hashes.json`. Read-only PDF/Word/rubric extraction is retained as `review/original_brief_text.txt`, `original_word_text.txt` and `original_marking_cells.txt`. PDF pages 2/3 were also rendered and visually inspected. No source document or workbook was modified.

## Task completeness

The actual original Task A/B/C wording and Word template agree with the earlier recovered requirements. The four numbered report headings and Figure 1–13/Table 1 mapping are correct. Retain the approved AIAA class and those headings. Task-specific caption/text limits remain applicable: A2 under 100 words, B3 description and Figure 6 description each no more than 150 words, each C1/C2 explanation at most 100 words (use the stricter under-100 brief wording where stated), C3 combined under 100 words, and C4 under 550 words. The brief's introductory context explicitly mentions a mesh-dependence check; changing both closure and wall treatment with the supplied enhanced mesh does not isolate spatial convergence.

The user-supplied FAQ is the explicit clarification for fixed profile x stations 0.05/0.10/0.20 m, the S–A wall-function oversight, actual intensity for fluctuation calculation, initial enhanced-RSM then enhanced-k–epsilon Case 4, iteration counts and honest nonconvergence reporting. It does not authorize copying another student's inlet speed. User speed remains 50.9 m/s.

## Page and appendix requirements

- Original PDF has **nine source pages**, ending with the assessment rubric.
- Page 2 explicitly asks for an **eight-page report with strict length limits**.
- Page 3 explicitly asks for an AI-usage summary appendix of at most **two pages**, addressing **seven points** in an AI-usage-log template.
- Page 3 refers to detailed AI guidance in **Appendix 1**, but neither that appendix nor the actual seven-point log template appears in this nine-page PDF or supplied Word template. The source files therefore still do not establish the official seven field labels or supplied guidance-table contents.
- Neither the brief nor the Word text explicitly resolves whether the AI appendix is included within the eight-page total. Do not state that ten total pages are approved. If all required content can remain legible within eight total pages including an appendix of at most two, that satisfies both written limits; otherwise record the unresolved accounting rule and verify it before final submission.
- The existing seven-field appendix can remain as the approved working structure, but must not be described as a verbatim official template without its missing source. Update its real date/tool/activity/prompt record for the current Windows work.
- Final page count and layout must be checked from an actual Overleaf compilation after figures and result text are complete. Source `clearpage` commands do not prove compliance. No local LaTeX compilation was performed in this review.

## Marking inconsistency preserved

The task/Word headings allocate A=16, B=34 and C=50. Original rubric workbook cells **C6=20, C10=30, C14=50**, matching the rubric image on PDF page 9. This is an internal assessment inconsistency, not an implementation error. Preserve the user's approved headings and fulfill every task rather than changing the section marks. Rubric high-band descriptions emphasize actual software skill, complete data/figures, accurate understanding, concise descriptive captions and clear presentation; they add no new numerical convergence threshold.

## Specified experimental curve now identified

Independently viewed `data/literature/brief_C4_lift.png` and `brief_C4_drag.png`, crops from actual PDF page 8. The requested series is **black filled circles, Sheldahl Re=3.6e5, NACA0012–2D**. At eight degrees, **CL approximately 0.81 and CD approximately 0.017** are defensible manual graphical readings. Approximate visual allowances +/-0.02 and +/-0.003 respectively are reasonable given graph/marker resolution; they are not statistical confidence intervals or precise tabulated data. The old report's approximate ordinates are now supported by the actual assignment plot, resolving that earlier source-availability concern.

The original Sandia experimental Figure 4 reading around CL=0.86–0.88 is a separate primary-source cross-check, not permission to replace the specified reproduced curve. Keep the discrepancy and source identity transparent. Do not combine a lift reading from one graph with a drag reading from another while describing both as one matched dataset.

At actual Case 1 Re=348454.7893, the signed relative difference from 360000 is approximately **-3.21 percent**, as used by the prepared report. That comparison is arithmetic against the specified figure legend; distinctions between nominal/effective Reynolds definitions and test-section corrections remain limitations.

## Current status

Original-source availability now supports complete task mapping and the specified C4 curve. Remaining source gaps are the absent official AI appendix/template and explicit report/appendix page accounting. These do not prevent the authorized simulations, exports, plots or local report preparation from proceeding. A complete final PDF has not yet been compiled or approved.
