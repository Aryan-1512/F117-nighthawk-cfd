"""Turn the raw GrabCAD F-117 STL (mm, many loose pieces) into a clean, watertight
half-aircraft in metres, SU2 axes: x nose->tail, y span (symmetry plane y=0), z up."""
import trimesh, numpy as np, collections, sys
import shapely.geometry as sg
from trimesh.creation import triangulate_polygon
SINK=float(sys.argv[1]) if len(sys.argv)>1 else 0.05   # m, push tail root into body
ZS=6540.7
def boundary_loops(mesh):
    F=mesh.faces; de=np.vstack([F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]])
    c=collections.Counter(tuple(sorted(e)) for e in de)
    nxt={a:b for a,b in (tuple(e) for e in de if c[tuple(sorted(e))]==1)}
    seen=set(); out=[]
    for s in list(nxt):
        if s in seen: continue
        L=[];v=s
        while v not in seen: seen.add(v);L.append(v);v=nxt[v]
        out.append(L)
    return out,nxt
def fan_cap(mesh):
    loops,nxt=boundary_loops(mesh); V=list(mesh.vertices); F=list(mesh.faces)
    for L in loops:
        P=mesh.vertices[L]; c0=P.mean(0); u,s_,vt=np.linalg.svd(P-c0); ax=vt[:2]
        Q=(P-c0)@ax.T
        poly=sg.Polygon(Q)
        if not poly.is_valid: print('  tail root polygon invalid in projection')
        v2,f2=triangulate_polygon(poly,engine='earcut')
        idx=[L[np.linalg.norm(Q-q,axis=1).argmin()] for q in v2]
        for tt in f2:
            a,b_,c_=idx[tt[0]],idx[tt[1]],idx[tt[2]]
            F.append([a,b_,c_])
    m2=trimesh.Trimesh(np.array(V),np.array(F)); trimesh.repair.fix_winding(m2); return m2
raw=trimesh.load('F-117S.STL')
parts=sorted(raw.split(only_watertight=False),key=lambda p:-len(p.faces))
body=parts[0]
V=body.vertices.copy(); V[np.abs(V[:,2]-ZS)<1.0,2]=ZS
b=trimesh.Trimesh(V,body.faces); b.merge_vertices(digits_vertex=1)
b.update_faces(b.nondegenerate_faces(height=1e-3)); b.remove_unreferenced_vertices()
on=np.all(np.abs(b.vertices[b.faces][:,:,2]-ZS)<1e-6,axis=1)
h=b.submesh([np.where((b.triangles_center[:,2]>ZS)&~on)[0]],append=True); h.merge_vertices()
loops,nxt=boundary_loops(h); V=list(h.vertices); F=list(h.faces)
for L in loops:
    P=h.vertices[L]
    if np.ptp(P[:,2])<1e-6:   # centre-line cut -> proper polygon triangulation
        v2,f2=triangulate_polygon(sg.Polygon(P[:,:2]),engine='earcut')
        idx=[L[np.linalg.norm(P[:,:2]-q,axis=1).argmin()] for q in v2]
        for t in f2: F.append([idx[t[0]],idx[t[1]],idx[t[2]]])
    else:                      # intake / exhaust openings -> flat lid
        c=len(V); V.append(P.mean(0))
        for v in L: F.append([nxt[v],v,c])
hc=trimesh.Trimesh(np.array(V),np.array(F)); hc.merge_vertices(); trimesh.repair.fix_normals(hc)
tail=[p for p in parts[1:3] if p.bounds[0,2]>ZS][0]
t=fan_cap(trimesh.Trimesh(tail.vertices,tail.faces).process()); t.merge_vertices(); trimesh.repair.fix_normals(t)
t.apply_translation([0,-SINK*1000,0])
# extend tail downward: also scale? just translate; check root inside body
u=trimesh.boolean.union([hc,t],engine='manifold')
W=u.vertices; N=np.c_[W[:,0],W[:,2]-ZS,W[:,1]]/1000.0
s=trimesh.Trimesh(N,u.faces); 
if s.volume<0: s.invert()
s.vertices[np.abs(s.vertices[:,1])<1e-6,1]=0.0
from scipy.spatial import cKDTree
E=set(map(tuple,s.edges_sorted)); pr=[p for p in cKDTree(s.vertices).query_pairs(0.02,output_type='ndarray') if tuple(sorted(p)) not in E]
print('sink',SINK,'wt',s.is_watertight,'vol',round(s.volume,3),'bodies',len(s.split()),'close non-adjacent pairs',len(pr),'min edge',round(s.edges_unique_length.min(),5))
s.export('f117_half.stl')
