# Exact five-cell identity finding

The user's visual concern is correct. Five suction-side cells have actual raw y+ below 30, but a single horizontal bracket is not an exact selector of them.

In increasing wall x, the selected cells are 7588 (23.96556544), 7316 (25.93608120), 69 (19.56839664), 7251 (21.53721692), and 2573 (22.27944689). Cell 6134 (32.77977224) lies between the first two along the wall and must remain unselected. The apex of cell 7578 (40.23124347) projects into the old bracket's left end. Consequently seven actual suction-side triangles overlap the old bracket's x-projection even though only five meet the criterion.

The five wall edges are 11444, 11446, 11447, 11448 and 11414 in the actual aerofoil_suction zone7. The missing edge11445 belongs to cell6134. Thus the selected wall-edge sequence comprises one isolated edge followed by four consecutive edges; it is not one continuous five-cell interval. All complete triangle vertices, actual cell centroids, wall-edge endpoints, raw values and face connectivity are recorded in `exact_five_cells.json`.

The earlier acceptance verified that the bracket encompassed the full selected set, but did not exclude unrelated triangles within its global projection. That visual acceptance was insufficient and is superseded for this annotation. The CFD values and the count five remain correct.

Replace the bracket with individual red annotations on precisely these five actual triangles, or five centroid markers with individually resolved leaders. A single narrower bracket cannot convey the missing intermediate cell correctly. Native scientific RGB, centring, physical size, axes, palette and scalar values must remain unchanged. Red annotations must be described as post-export identification marks, not native Fluent cell colours.
