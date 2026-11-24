import pymeshlab as ml, trimesh, numpy as np, collections, sys
L=float(sys.argv[1]) if len(sys.argv)>1 else 0.12
ms=ml.MeshSet(); ms.load_new_mesh('f117_half.stl')
ms.meshing_merge_close_vertices(threshold=ml.PureValue(0.003))
ms.meshing_remove_duplicate_faces(); ms.meshing_remove_null_faces()
ms.meshing_isotropic_explicit_remeshing(iterations=15, targetlen=ml.PureValue(L), featuredeg=20, adaptive=False, checksurfdist=True, maxsurfdist=ml.PureValue(0.004))
ms.save_current_mesh('f117_half_remesh.stl')
m=trimesh.load('f117_half_remesh.stl')
c=collections.Counter(map(tuple,m.edges_sorted))
t=m.triangles
def ang(t):
    a=np.linalg.norm(t[:,1]-t[:,2],axis=1);b=np.linalg.norm(t[:,0]-t[:,2],axis=1);cc=np.linalg.norm(t[:,0]-t[:,1],axis=1)
    A=np.degrees(np.arccos(np.clip((b*b+cc*cc-a*a)/(2*b*cc),-1,1)));B=np.degrees(np.arccos(np.clip((a*a+cc*cc-b*b)/(2*a*cc),-1,1)))
    return np.minimum(np.minimum(A,B),180-A-B)
ma=ang(t)
print('L',L,'faces',len(m.faces),'wt',m.is_watertight,'edgeuse',dict(collections.Counter(c.values())),'vol',round(m.volume,3),'bounds',np.round(m.bounds,3).tolist())
print('  minangle<10:',(ma<10).sum(),'min',round(ma.min(),3),'sym verts off-plane',((np.abs(m.vertices[:,1])<0.01)&(np.abs(m.vertices[:,1])>1e-9)).sum())
