# Task A coordinate inspection

`geometry_coordinate_check.svg` is an independently drawn diagram of the actual CSV coordinates exported during native SpaceClaim geometry creation. It is not a Discovery screenshot, a mesh view or a flow solution. The matching PNG is rendered from that SVG for convenient inspection. Actual software geometry imagery should take priority when the report requires evidence of geometry construction.

`../plot_taskA_geometry.py` reads the original CSV files without changing them. It verifies the two surface endpoints against native boundary edge endpoints, planarity, the seven names, 1 m by 0.15 m duct, chord length, rotation, surface symmetry after undoing the rotation, and the actual finite trailing-edge closure. Both diagram panels retain equal horizontal and vertical scales. The local panel is enlarged relative to the full duct.

The measured chord vector points 8 degrees clockwise from +x, giving positive 8-degree physical incidence for flow entering along +x. The leading edge is (0, 0) m and the trailing-edge centre is (0.099026806874157, -0.013917310096007) m. The chord is 0.1 m. The 0.252 mm finite trailing edge is closed by the actual `aerofoil_te` boundary; it is not collapsed to a sharp point in this diagram.

`geometry_check_audit.json` contains source and script SHA256 hashes, measured properties, boundary names and the SVG hash. A separate PNG render manifest records its SVG source hash and rendering library. No fluid properties or CFD solution values enter this geometry diagram.
