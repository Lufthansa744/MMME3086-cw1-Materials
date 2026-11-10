# Centered native artwork

This directory contains new Fluent-native exports for Figure 5 and Figure 6(a) only. Earlier native raw files and the selected Figure 2, Figure 4 and Figure 6(b/c) layers remain unchanged.

Figure 5 keeps the same 0.116 by 0.038 m orthographic field and x centre 0.05 m. Its y centre is now the actual 103-node foil-boundary bounding-box midpoint, 0.0015294034661851664 m. The y-plus field, flat cell values, light-gray native mesh context, black foil outline and native scalar range are unchanged.

Figure 6(a) keeps the same 0.24 by 0.055 m field and printed size. Its x centre changes from 0.11 to 0.05 m. Twelve native rake surfaces with 45 requested points were regenerated over the new world coordinates; the native export contains **506 valid points**, rather than the earlier 504. Arrows remain native 75-microsecond scale, filled 3D style, head scale 0.4, velocity colors 0–120 m/s and 4-pixel hardcopy outline. About 0.705 chord remains downstream of the TE. The x=0.2 m reporting station is outside this view.

The new sampling CSV is native node-interpolated ASCII evidence. It is not asserted numerically identical to every internal vector-renderer sample. No native pixels were shifted, no upstream field was fabricated, and no arrows or cell fills were externally redrawn. Native EPS files may contain raster sections.

`scripts/centered_native_executed.jou` was actually launched through `-i` in one fresh graphics-enabled Fluent process and executed to EOF without errors. The separately saved shutdown command block was then executed through the same TUI. No extra identical replay was performed after artwork creation. The exact OS command is in `scripts/launch_centered_graphics.ps1`; logs and Windows process command lines are under `logs`.

All four source CASE/DATA hashes match before and after postprocessing. No initialization, iterations, physical-setting changes, mesh edits or source writes occurred. Fluent exited normally and its numerical processes were released. See `CENTERED_NATIVE_MANIFEST.json`, `geometry_window_audit.json` and `native_sampling_audit.json` for parameters, file hashes and the validation scope.
