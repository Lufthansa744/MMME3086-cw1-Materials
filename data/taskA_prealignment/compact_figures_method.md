# Compact Task A report figures

Use `figure1_native_compact.png` and `figure2_mesh_compact.png` for the report; original PNGs and vector SVGs remain separate. The PNGs are 3200 by 1060 and 3200 by 1480 pixels respectively. Their dimensions and readable type are designed for the report's full text width, not a single narrow column. Figure 1 is about 45 mm high at 136 mm wide, with approximately 7.7 pt minimum text. Figure 2 at 170 mm wide is 78.6 mm high, with minimum text 8.43 pt. Final legibility must still be checked in the actual Overleaf PDF.

Figure 1 contains the actual native SpaceClaim `Window.Export` raster views. Only blank margins are cropped; each panel is placed with uniform scaling. Neither the background nor the body outline is redrawn or recolored. Added dimensional/chord/AoA marks are annotations on the native geometry, supported by the actual geometry export script and dense CAD coordinates. Exact crop boxes, panel scales, source hashes and annotation transform are in `compact_figures_manifest.json`.

Figure 2 draws the actual exported mesh's node-to-node face segments directly. It preserves the exact irregular elements, seven boundary names and the finite trailing-edge boundary. Both views have equal horizontal and vertical scales. It does not impersonate an Ansys screenshot; its caption should describe it as a plot of the actual native mesh. The source mesh hash matches the independent review audit. The larger audit/checking figures remain available, with counts and longer methods.

Reproduce the self-contained SVGs with the bundled Python runtime (Pillow and NumPy required):

```powershell
python data/make_taskA_compact.py
```

The PNGs were rasterized from these SVGs with the bundled `sharp` package at density 144. This rendering does not compile LaTeX. Both PNGs were visually inspected with no clipped labels or overlapping annotation text.
