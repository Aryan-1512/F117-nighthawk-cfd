"""Full-aircraft domain: mirror the cleaned half F-117 across y=0, join the halves,
and surround it with a closed far-field box. Output: f117_full_domain.stl"""
import trimesh, numpy as np, collections, gmsh
X0,X1,Y0,Y1,Z0,Z1 = -60.0, 100.0, -60.0, 60.0, -60.0, 60.0
H_FAR=8.0
m=trimesh.load('f117_half_remesh.stl')
on=np.all(np.abs(m.vertices[m.faces][:,:,1])<1e-9,axis=1)          # drop the cut face
half=m.submesh([np.where(~on)[0]],append=True)
mirror=half.copy(); mirror.vertices[:,1]*=-1; mirror.invert()        # mirror image
full=trimesh.util.concatenate([half,mirror]); full.merge_vertices(digits_vertex=7)
c=collections.Counter(map(tuple,full.edges_sorted))
print('aircraft faces',len(full.faces),'edgeuse',dict(collections.Counter(c.values())),'wt',full.is_watertight,'vol',round(full.volume,3))
full.export('f117_full.stl')
gmsh.initialize(); gmsh.option.setNumber("General.Verbosity",2)
gmsh.model.occ.addBox(X0,Y0,Z0,X1-X0,Y1-Y0,Z1-Z0); gmsh.model.occ.synchronize()
gmsh.option.setNumber("Mesh.MeshSizeMin",H_FAR); gmsh.option.setNumber("Mesh.MeshSizeMax",H_FAR)
gmsh.model.mesh.generate(2); gmsh.write('box.stl'); gmsh.finalize()
box=trimesh.load('box.stl'); box.invert()   # normals don't matter for gmsh, keep consistent
dom=trimesh.util.concatenate([full,box])
print('domain faces',len(dom.faces))
dom.export('f117_full_domain.stl')
