# Experimental reference evidence review

Current status: the original brief is now available as `inputs/MMME3086-CFD-V2.0.pdf`. Its printed page 8 explicitly identifies the required black filled-circle curve as Sheldahl, Re=3.6e5, NACA0012–2D. Direct reading of that actual curve at 8 degrees gives CL about 0.81 and CD about 0.017. These numbers now have source evidence; they are not retained merely because an old report used them. Conservative manual reading allowances are ±0.02 for CL and ±0.003 for CD, not statistical confidence intervals. The original page and enlarged PDF renders are `brief_page8.png`, `brief_C4_lift.png` and `brief_C4_drag.png`. See `brief_reference_reading.json` for hashes and crop coordinates.

The earlier primary-Sandia investigation below remains a cross-check, not a replacement for the specific reproduction the brief instructs students to use. Its near-8-degree lift reading differs from the brief's reproduced curve. Preserve that source distinction explicitly. The Overleaf template image `graph.jpg` is a magnetization curve and remains excluded.

## Sources and access

* [Martínez-Aranda et al. (2016), DOI 10.5923/j.aerospace.20160401.01, paper copy](https://scispace.com/pdf/comparison-of-the-aerodynamic-characteristics-of-the-2dz69euprm.pdf): web text accessible, including printed pp.1–5; actual figure images unavailable through the tool. Direct mirror download returned HTTP403; publisher timed out. No usable local PDF of this paper was obtained
* [Sheldahl and Klimas (1981), SAND80-2114, original Sandia report archive](https://digital.library.unt.edu/ark:/67531/metadc1191254/), DOI 10.2172/6548367: complete 124-page scan saved as `sheldahl_klimas_1981.pdf` from the archive's [PDF endpoint](https://digital.library.unt.edu/ark:/67531/metadc1191254/m2/1/high_res_d/6548367.pdf). This is a primary research source, not a later synthetic online polar

## What the 2016 text establishes

Printed p.1 identifies the Sheldahl/Klimas 2D comparison at Re between 3.6e5 and 7e5. Printed pp.2–3 describe the 2016 authors' own experiment: chord 100 mm, span 200 mm, AR=2 and a 1 m² tunnel cross section. That is a different model from Sheldahl's experiment and cannot be cited as Sheldahl's geometry. The 2016 drag and lift comparisons are Figures 3 and 4, printed pp.4 and 5. Their direct paper images could not be fetched, but their reproduction on the newly supplied assignment page 8 has now been inspected and provides the required coursework reference identified above.

## Original Sandia report: inspected pages

| Printed page / PDF page | Evidence |
|---|---|
| 9 / 12 | Aluminum test models: 6 in (152.4 mm) chord, 3 ft (about 0.91 m) span; separate larger wooden model |
| 10 / 13 | Main tunnel 7 by 10 ft; two-dimensional inserts create 3 ft wide by 7 ft high section, about 0.91 by 2.13 m; models attached to end plates; corrected measurements and turbulence factors described |
| 11 / 14 | Experimental force-drag correction using a wake survey; explicit discussion of combining measured data with computed section properties |
| 78 / 81 | Figure 4: experimental NACA0012 lift, Re=0.36e6 and 0.70e6; increasing/decreasing incidence indicated |
| 88 / 91 | Figure 14: experimental small-angle NACA0012 drag, Re=0.36e6, 0.50e6 and 0.70e6 |
| 19 / 22 and 20 / 23 | Table 2 contains Eppler/hybrid tabulation, not an unqualified table of measured experimental ordinates |

The scan has been rendered to the `sheldahl_pdf_page_*.png` files. Detailed lift/drag render crops are provided for inspection. Full pages preserve axes, legend and captions; crops are only aids to viewing.

## Preliminary manual reading of the original experimental figures

| Source | Re | Coefficient at approximately 8 degrees | Estimated visual reading allowance |
|---|---:|---:|---:|
| Original Figure 4 | 0.36e6 | CL about 0.86 | ±0.03 |
| Original Figure 4 | 0.70e6 | CL about 0.89 | ±0.03 |
| Original Figure 14 | 0.36e6 | CD about 0.017 | ±0.001 |
| Original Figure 14 | 0.50e6 | CD about 0.015 | ±0.001 |
| Original Figure 14 | 0.70e6 | CD about 0.016–0.017 | ±0.001 |

These are manual interpolative readings of the scanned curves/nearby symbols, not exact data or a statistical confidence interval. Marker width, scan quality, identifying the branch and interpolating at exactly 8 degrees limit the reading. They are cross-checks of the original experiment only. They do not identify which curve the coursework brief reproduced and must not silently replace the brief's comparison value. FAQ Q20 accepts doing what is possible with poor resolution; describe the reading limitation honestly.

The independent review agent inspected the same full figure scans and apparatus pages. Its visual ranges were approximately CL=0.86–0.88 for Re=0.36e6 and 0.89–0.91 for Re=0.70e6, agreeing with the conservative allowances above; its drag reading also agreed. It independently confirmed the end plates and two-dimensional inserts. This cross-check does not resolve the missing brief-curve identity. Preserve the figure legend's Re=0.36e6 while noting the main text calls the lower condition nominally 0.35e6; do not silently convert or relabel Reynolds numbers.

For contrast, Table 2 lists CL=0.8542, CD=0.0153 at Re=360000 and CL=0.8800, CD=0.0128 at Re=700000 for 8 degrees. The table's Eppler/hybrid construction is explained on printed p.11 and in its headers. These tabulated values must not be relabelled as the Figure 4/14 measured points. Online NACA0012 polar files may reproduce or further alter such tables.

## Consequences for later comparison

Use the actual CFD density and viscosity to calculate its Reynolds number. Compare the chosen experimental curve and its documented Reynolds definition. Sandia corrected wind-tunnel results for blockage, buoyancy, upwash and wind-turbulence effects; its effective-Re turbulence factors are stated on printed p.10. Matching a nominal Reynolds number alone does not reproduce its boundary conditions.

The CFD duct height is 0.15 m for a 0.1 m chord, so H/c=1.5. Sandia's 2.13 m test-section height and 0.1524 m chord give H/c about 14. Its side inserts/end plates seek two-dimensional section behavior. Do not describe that setup as an unconfined finite AR=6 wing with unrestricted tip vortices merely because span/chord is near 6. The 2016 authors' AR=2 wing study addresses a different three-dimensional arrangement.

The original missing-brief condition has been resolved. Use the actual brief reproduction's black filled-circle Re=3.6e5 series for the requested C4 comparison, with clearly stated graphical reading precision. A second independent reading has been requested from the review agent. No CFD/experiment error is computed in this document; per-case comparison calculations use validated outputs and this declared reference in their own auditable records.
