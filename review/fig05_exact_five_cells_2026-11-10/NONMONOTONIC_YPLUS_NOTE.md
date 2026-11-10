# Why the selected cells can skip a neighbour

The five red selections remain correct. Applying a threshold to a local quantity need not select a continuous sequence along the wall. In the actual suction-wall order, cell 6134 has y+ = 32.77977 and falls between selected cells 7588 (23.96557) and 7316 (25.93608). It is therefore correctly unmarked.

Independent measurements from actual mesh vertices and saved cell centroids give perpendicular distances to each cell's own wall edge of 0.723106 mm for 6134, 0.569225 mm for 7588 and 0.653013 mm for 7316. The skipped cell centre is 27.03% farther from its wall edge than 7588 and 10.73% farther than 7316. The corresponding y+ increases are 36.78% and 26.39%. Irregular first-cell spacing provides a plausible contribution, but is not the whole explanation: the diagnostic y+/geometric-distance ratio also differs by 7.67% and 14.14%.

These are direct geometric distances, not newly exported Fluent wall-distance or wall-shear fields. They support a reasonable local variation and correct threshold selection; they do not independently measure the exact shear contribution. Do not claim that local wall shear was proven to jump or assign a particular flow mechanism without its actual field.

Non-monotonic y+ is not itself an annotation error. The five cells below 30 still identify a wall-treatment suitability concern in this coarse standard-wall-function case. Neither their count nor these ratios proves convergence, mesh accuracy or grid independence. No change to the published figure is indicated.
