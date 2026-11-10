# MMME3086 CFD coursework — Windows computation and Mac continuation

Student **20617209** · inlet **50.9 m/s** · five prescribed cases complete.

**10 November native-artwork update:** For the current Mac report, start with [the native Figure 2/4/5/6 handoff](report/native_fluent_2026-11-10/MAC_NATIVE_FIGURE_HANDOFF.md). It preserves the attached Mac PDF's exact artwork boxes, uses native Fluent scientific layers and keeps Figure 1's verified native SpaceClaim pictures. Replace the selected artwork only; the historical Windows source ZIP below must not overwrite the newer Mac report. Native images, reproducible display controls and independent checks accompany the new assets. Report compilation remains an Overleaf-only step on Mac.

The historical [Windows handoff](MAC_HANDOFF.md) records the numerical work and independent content review. Its source uses the approved AIAA class and thirteen figures; that Windows package was not compiled locally. The newer nine-page Mac PDF supplied on 10 November is the layout reference for the native-artwork update. **After replacing the artwork, compile and inspect the updated report only in the approved Overleaf project.**

## Historical Windows source package

Figure 2 artwork was corrected on 7 November: the outlet label and 150 mm dimension are separated, and the bottom axis label has clear canvas margins. Mac can replace the single active asset, `report/prepared/fig02_mesh_bc.png`; the source ZIP includes the same correction. See `review/figure2_annotation_review.md`.

- [Overleaf source ZIP](report/LIU_Yang_20617209_CFD_Overleaf_Source.zip) — upload to the existing approved project; do not substitute an older snapshot or create a different template.
- [Prepared main source](report/prepared/main.tex) and [result table](report/prepared/verified_table.tex).
- [Source package status](report/source_package_status.json), [independent content review](review/final_report_content_review.md), [vector/layout review](review/layout_and_vector_review.md).
- [Original-data delivery manifest](data/final_data_manifest.json), [print-asset audit](data/print_assets/print_asset_audit.json), [vector PDF independent audit](review/vector_pdf_independent_audit.json).

## Formal final datasets

| Coursework case | Physical folder | Numerical disposition |
|---|---|---|
| 1 S–A | `solver/case01_aligned` | Supplementary strict targets pass |
| 2 standard k–epsilon | `solver/case02_aligned` | Qualified; continuity plateau retained |
| 3 RSM | `solver/case03_aligned` | Qualified; continuity plateau retained |
| 4 k–epsilon EWT | `solver/case04_verified` | Supplementary strict targets pass |
| 5 relaxed RSM EWT | `solver/case05_verified` | Supplementary strict targets pass; counts distinguish added RSM updates from inherited KE history |

The authoritative mapping is [dataset_registry.json](data/dataset_registry.json); [final_case_index.json](coordination/final_case_index.json) links the actual final case/data files and summaries. Historical prealignment/early-stop cases and workbooks are retained for traceability and are excluded from the final five-case comparison.

## Evidence and native projects

- `inputs/`: supplied brief, template, marking sheet, enhanced mesh and FAQ, with provenance/hashes.
- `solver/`: native geometry/meshes, executable journals, saved settings, Case/Data, transcripts, monitors, raw field/force exports, initial enhanced RSM and separate auxiliary studies.
- `solver/workbench/final_coursework_cases.wbpj` **and its matching `_files` directory**: final five-system project. Stored solution copies match the original final files. If moved to another root, Setup source references may need relinking; see [recovery audit](solver/final_recovery_storage_audit.json). No `.wbpz` archive is claimed.
- `data/`, `outputs/`: processed data, figures, scripts, five formal and three auxiliary verified Excel workbooks, and checks.
- `review/`: independent numerical, geometry, field-mapping, force, source and print checks.
- `coordination/`: requirements, decisions, acceptance policy, handoff and browser diagnostic records.

Three-grid sensitivity does **not** establish spatial independence. The inlet-length contrast tests a recorded input assumption, not a calibrated experimental condition. Reference CL/CD values are graphical estimates with different confinement; no case is declared experimentally validated merely because its forces stabilised.

Runtime dependencies, machine caches, credential stores and linked `node_modules` are not coursework evidence and are excluded. Original evidence is preserved. The repository manifest records file sizes and SHA256 hashes; a successful Git upload does not certify the outstanding Overleaf compilation or rendered-page checks.
