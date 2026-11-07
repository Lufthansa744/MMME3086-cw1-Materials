# Independent final Figure 2 annotation review

PASS. The final 165.1 mm wide, 300 dpi print-size preview was independently viewed. The outlet label is clearly separated from the relocated 150 mm dimension arrow and rotated dimension label. The witness lines are readable. The dimension label and the complete bottom x(mm) parentheses are inside the canvas; the axis label does not overlap the 50 tick label.

Two minimal annotation changes are accepted: (1) relocate/reorient the height-dimension annotation with witness lines; (2) move the bottom x(mm) baseline from736 to730 to correct independently confirmed pre-existing clipping. Font sizes, canvas and scientific content were preserved.

Removing exactly the old four annotation elements and final five annotation elements leaves byte-identical SVG XML. This checks every mesh path, coordinate transform, inset, seven boundary labels, colours and remaining font attributes. Canvas remains1600 by740; PNG remains3200 by1480. All changed decoded PNG pixels fall within the exact height-dimension ROI or bottom-axis-label ROI; outside these regions pixel changes are zero. Original mesh SHA256 remains614e5eee90b0cadab2ba590711e98d79e9f02555f64c6881780ad099e02293be.

The outlet ink ends near x1509 SVG px, while the conservatively bounded leftmost arrow ink starts x1535:26 px clearance. The rotated 150 mm ink bounds are approximately[1565,126.5,1585,228.5], inside the canvas. The shifted x(mm) ink bounds are approximately[774.5,710,860.5,736]; the measured last dark PNG row is1471, leaving8 blank rows. Both labels retain28 SVG px, equivalent to8.19 pt at165.1 mm report width.

Final SVG SHA256:3338c73028e169a401135087184f65fbc97b3d043481179e49d31f545be7baaf

Final PNG SHA256:6d1f52775cef64a532b3e533d15e9cbd314e7e40a4743fac1b17f0666ac96b7f

Machine-readable final checks are in figure2_annotation_review_audit.json; pre-change identities and original SVG/PNG snapshots are retained independently. The intermediate height-only disposition is preserved in figure2_annotation_review_height_only_audit.json and is superseded for delivery by this final corrected asset. The mesh and CFD results were not rerun or modified. No local TeX compilation was performed; rendered Overleaf pagination remains outside this image-level acceptance.
