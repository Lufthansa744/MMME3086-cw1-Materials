# Continue the report on Mac

**10 November update supersedes the source-upload steps below for the current Mac document:** Read [MAC_NATIVE_FIGURE_HANDOFF.md](report/native_fluent_2026-11-10/MAC_NATIVE_FIGURE_HANDOFF.md), then replace only the new Figure 2/4/5/6 artwork. Retain the newer Mac Overleaf source, template, sections and AI appendix. Figure 1's native SpaceClaim pictures remain. The historical instructions and source ZIP below are retained as provenance, not an instruction to overwrite the Mac report.

## Next action

1. Clone/download this repository and read `report/source_package_status.json` and `review/layout_and_vector_review.md`.
2. In the Mac chat, use the authorised browser interface to check the **existing** approved Overleaf project: https://www.overleaf.com/project/6aed174c208587f797ee667b . If its own site gate refuses access, stop that browser route and resolve the permission through supported controls.
3. Upload `report/LIU_Yang_20617209_CFD_Overleaf_Source.zip` contents to that project, retaining `main.tex` as the main document. The ZIP is self-contained. `report/prepared/` also contains older PNGs for preservation; the active `main.tex` explicitly uses PNG for Figures 1–2 and PDF for Figures 3–13.
4. **Compile only in Overleaf.** Download the actual PDF and inspect every page. Resolve compile errors, undefined references, font/glyph problems, overfull content, figure/table/caption breaks and the required eight-page limit. Recompile there after each source change. Do not claim final layout approval from the present static review.

## Preserve these requirements

The latest Figure 2 correction is available as `report/prepared/fig02_mesh_bc.png` and `data/taskA/figure2_mesh_compact.svg`. To update a report already edited in Overleaf, replace the existing `fig02_mesh_bc.png` with this corrected asset. The updated source ZIP also includes it.

- Approved `new-aiaa.cls`, the four prescribed section headings, figure numbering/order and reported values. Natural continuous pagination now replaces seven forced page breaks; actual page count is not yet verified.
- No `working draft`, `TODO` or unresolved fields in submitted prose. No punctuation after displayed equations.
- Course word limits: mesh caption <100; B3 explanation/caption <150 each; C1 each plot analysis <100; C2 each analysis <100; C3 combined explanation <100; C4 comparison <550. Current text has passed source review.
- Formal inputs: rho=1.225 kg/m³, mu=1.7894e-5 Pa·s, U=50.9 m/s, I=5%, selected inlet L=1 m, chord=0.1 m, unit span and reference area=0.1 m². The length scale is an observed software input, not measured tunnel turbulence.
- Cases 2/3 missed the supplementary 1e-5 continuity target despite stable forces. Preserve qualified flags and explicit limitations. Case 5 table counts 984/2936 **new RSM updates**, inherited KE seed=753; corresponding global counts=1737/3689.
- Three-mesh drag still changes 4.79% medium-to-fine; lift is non-monotonic. No grid-independence or invented GCI claim. Inlet L=0.01 m auxiliary contrast is separate from the five-case table and is not calibration.
- Reference readings CL≈0.81/CD≈0.017 are approximate brief-curve readings, not exact tabulated measurements. The duct confinement differs materially from the experiment.

## What is already complete

Task A geometry/mesh, five formal cases, initial enhanced RSM diagnostic, two supplementary S–A mesh levels and inlet-length contrast; settings, native histories, paired final Case/Data, monitors and original exports; thirteen original-data figures and eight verified Excel workbooks. Eleven scientific plots now have directly source-derived, embedded-font vector PDF versions independently checked against original SVG/PNG. No original SVG, PNG or numerical sample was changed by that conversion.

No Fluent recomputation is needed merely to resume report compilation. Native Windows Workbench files and all evidence are included for preservation; this does not imply that Ansys can run natively on Mac. Relocate any absolute Setup references only when opening the project in a compatible Ansys environment.

## Why the Windows browser work stopped

Both Edge and Chrome could be discovered and their Overleaf tabs listed. Page observation was rejected before any upload/edit/compile. Read-only diagnostics showed the exact Overleaf origin allowed globally but denied in the old conversation's stored state. No permission files or browser security controls were changed. Similar public reports and a sanitised reproduction are under `coordination/overleaf_permission_reproduction.md`. A new chat must pass its own supported access check; it is not guaranteed to inherit the old denial or to resolve every policy issue.

## Suggested Mac-chat prompt

> 继续此仓库的 MMME3086 CFD 报告。先读 README.md、MAC_HANDOFF.md、report/source_package_status.json 和最终审查记录。使用已批准的现有 Overleaf 项目，我授权上传课程源码/图表、编辑并编译该项目，不向学校或 AIAA 提交。只在 Overleaf 编译；先验证浏览器权限。保留已审查数值、AIAA 模板与规定 sections，不重算 CFD。逐页检查实际 PDF 并修正到满足页数、图表可读性和所有任务要求，再交付最终 PDF 与匹配源码。
