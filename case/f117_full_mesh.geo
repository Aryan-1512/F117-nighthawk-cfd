// ===================================================================
//  F-117 FULL-model volume mesh for SU2  (Gmsh .geo script)
//  Input : f117_full_domain.stl = aircraft surface + closed far-field box
//  Use   : open this file in Gmsh -> Mesh > 3D -> File > Export (.su2)
//  Units : metres. Axes: x nose->tail, y span (left -, right +), z up.
// ===================================================================

// --- far-field box limits (must match the boundary STL) -------------
X0 = -60; X1 = 100; Y0 = -60; Y1 = 60; Z0 = -60; Z1 = 60;
eps = 1e-3;

// --- mesh sizes -----------------------------------------------------
h_wall = 0.12;   // cell size at the aircraft surface [m]
h_far  = 8;      // cell size far away from the aircraft [m]
d_grow = 45;     // distance over which cells grow from h_wall to h_far [m]
h_near = 0.35;   // max cell size in the zone close to the aircraft [m]
d_near = 4;      // thickness of that close zone [m]

// 1) Read the triangulated boundary
Merge "f117_full_domain.stl";

// 2) Split it into patches wherever the surface bends by more than 40 deg,
//    so the aircraft panels and the six box faces become separate surfaces.
//    We keep the existing triangles (no re-parametrisation).
ClassifySurfaces{40*Pi/180, 1, 0, Pi};
CreateTopology;

// 3) Identify the boundary types by where they are
far[]  = Surface In BoundingBox{X0-eps, Y0-1, Z0-1,  X0+eps, Y1+1, Z1+1};   // inflow face
far[] += Surface In BoundingBox{X1-eps, Y0-1, Z0-1,  X1+eps, Y1+1, Z1+1};   // outflow face
far[] += Surface In BoundingBox{X0-1, Y0-eps, Z0-1, X1+1, Y0+eps, Z1+1};   // side face (-y)
far[] += Surface In BoundingBox{X0-1, Y1-eps, Z0-1, X1+1, Y1+eps, Z1+1};   // side face (+y)
far[] += Surface In BoundingBox{X0-1, Y0-1, Z0-eps,  X1+1, Y1+1, Z0+eps};   // bottom face
far[] += Surface In BoundingBox{X0-1, Y0-1, Z1-eps,  X1+1, Y1+1, Z1+eps};   // top face
all[]  = Surface{:};
wall[] = all[];
wall[] -= {far[]};
Printf("surfaces: wall %g, farfield %g", #wall[], #far[]);

// 4) The air volume = everything enclosed by these surfaces
Surface Loop(1) = {all[]};
Volume(1) = {1};

// 5) Boundary names -> become SU2 markers
Physical Surface("WALL")     = {wall[]};
Physical Surface("FARFIELD") = {far[]};
Physical Volume("FLUID")     = {1};

// 6) Cell size: small near the aircraft, growing with distance
Field[1] = Distance;
Field[1].SurfacesList = {wall[]};
Field[2] = Threshold;
Field[2].InField  = 1;
Field[2].SizeMin  = h_wall;
Field[2].SizeMax  = h_far;
Field[2].DistMin  = 0.05;
Field[2].DistMax  = d_grow;
// Field 3: inside a close zone around the aircraft, cells may not exceed h_near
//          (this is where the shocks and vortices are). Outside it: no limit.
Field[3] = Threshold;
Field[3].InField  = 1;
Field[3].SizeMin  = h_wall;
Field[3].SizeMax  = h_near;
Field[3].DistMin  = 0.05;
Field[3].DistMax  = d_near;
Field[3].StopAtDistMax = 1;
// Final size = the smaller of field 2 and field 3 at every point
Field[4] = Min;
Field[4].FieldsList = {2, 3};
Background Field = 4;
Mesh.MeshSizeExtendFromBoundary = 0;
Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;

// 7) Mesher settings
Mesh.Algorithm3D = 1;     // Delaunay tetrahedra
Mesh.Optimize = 1;        // improve bad tetrahedra
Mesh.SaveAll = 0;         // only save the named (physical) parts
