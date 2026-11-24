# Geometry preparation

The downloaded F-117 STL was not usable for CFD as-is: it was split into 79 loose pieces, had six open holes (intake grilles, exhaust slots, a collapsed wing-tip loop), duplicate faces down the centre line and sliver triangles. These scripts turn it into the closed, meshable surface `f117_full_domain.stl` that `case/f117_full_mesh.geo` reads. Copy that file into `case/` after running them.

Run them in order, in a folder that contains the original `F-117S.STL` (from the GrabCAD model linked in the main README):

| Script | What it does |
|---|---|
| `prep.py` | Keeps the main body and tail fins, drops the loose fragments, cuts the body on its centre line, caps the intake and exhaust openings flat, sinks each tail fin 5 cm into the body so the two join without hairline cracks, merges them, and converts to metres with SU2 axes (x nose to tail, y span, z up). Writes `f117_half.stl`. |
| `remesh.py` | Rebuilds the surface as evenly sized triangles (about 12 cm) while keeping the sharp panel edges. Writes `f117_half_remesh.stl`. |
| `build_boundary_full.py` | Mirrors the half aircraft across the centre line, joins the halves and surrounds it with a 160 m x 120 m x 120 m far-field box. Writes `f117_full_domain.stl`, the input for `case/f117_full_mesh.geo`. |

Requirements: `pip install trimesh numpy scipy shapely mapbox_earcut manifold3d pymeshlab gmsh`
