from common import *
import os, sys
import sys; D=(sys.argv[1].rstrip('/')+'/') if len(sys.argv)>1 and not sys.argv[1] in ('top','iso','slices','stream','mesh') else 'case/'
O='images/'; os.makedirs(O,exist_ok=True)
s=read(D+'surface_flow.vtu').extract_surface(algorithm='dataset_surface'); s.set_active_scalars('Pressure_Coefficient')
cp=dict(scalars='Pressure_Coefficient',cmap='coolwarm',clim=[-1.2,1.2])
mach=dict(scalars='Mach',cmap='coolwarm',clim=[0.4,1.2])   # white = free-stream Mach 0.8
which=[a for a in sys.argv[1:] if a in ('top','iso','slices','stream','mesh')] or ['top','iso','slices','stream','mesh']
c=np.array([9.6,0,1.4])
if 'top' in which:
    p=plotter(); p.add_mesh(s,**cp,scalar_bar_args=sbar('Pressure coefficient'),lighting=False)
    title(p,'F-117: pressure on the upper surface','Mach 0.80, 3° angle of attack. Each flat panel has its own pressure; low-pressure bands form along the panel edges.')
    cam(p,c+[0,0,40],c,up=(0,1,0),parallel=True); p.camera.parallel_scale=8.6
    p.screenshot(O+'f117_cp_top.png'); p.close()
if 'iso' in which:
    p=plotter(); p.add_mesh(s,**cp,scalar_bar_args=sbar('Pressure coefficient'),ambient=0.35,diffuse=0.7,specular=0.0)
    title(p,'F-117: surface pressure','High pressure at the nose (red), suction over the upper panels (blue), recovery toward the tail.')
    cam(p,(-12,-17,13),(11.5,0.8,1.2)); p.camera.zoom(1.12)
    p.screenshot(O+'f117_cp_iso.png'); p.close()
if 'slices' in which:
    f=read(D+'flow.vtu')
    for y,name,t,sub in [(0.0,'f117_mach_centreline','F-117: Mach number on the centre line','White is the free-stream speed (Mach 0.8). Red is faster, blue slower: the air speeds up over the cockpit and slows at the nose and tail.'),
                         (3.0,'f117_mach_wing','F-117: Mach number on a cut through the wing, 3 m from the centre line','White is the free-stream speed (Mach 0.8). Faster air above the wing than below means lower pressure on top: that difference is lift.')]:
        sl=f.slice(normal=(0,1,0),origin=(5,y,1)).clip_box([-1.3,21.9,y-0.5,y+0.5,-3.6,4.6],invert=False)
        p=plotter(); p.add_mesh(sl,**mach,scalar_bar_args=hbar('Mach number'),lighting=False)
        body=s.slice(normal=(0,1,0),origin=(5,y,1))
        p.add_mesh(body,color='#1d2733',line_width=3)
        title(p,t,sub)
        sc=np.array([10.3,y,0.6]); cam(p,sc+[0,-60,0],sc,up=(0,0,1),parallel=True); p.camera.parallel_scale=6.6
        p.screenshot(O+name+'.png'); p.close()
if 'stream' in which:
    f=read(D+'flow.vtu'); f.set_active_vectors('Velocity')
    seeds=None
    for z in (0.7,1.3):
        l=pv.Line((-4,-7.5,z),(-4,7.5,z),resolution=24); seeds=l if seeds is None else seeds.merge(l)
    st=f.streamlines_from_source(seeds,vectors='Velocity',max_length=29,integration_direction='forward')
    p=plotter(); p.add_mesh(s,color='#9aa6b2',ambient=0.3,diffuse=0.7)
    p.add_mesh(st.clip_box([-10,23,-20,20,-20,20],invert=False).tube(radius=0.03),**mach,scalar_bar_args=sbar('Mach number'))
    title(p,'F-117: streamlines coloured by Mach number','White is the free-stream speed (Mach 0.8). The air splits at the nose, speeds up over the faceted body and leaves past the V-tail.')
    cam(p,(-13,-15,11),(11,0,1.0)); p.camera.zoom(1.05)
    p.screenshot(O+'f117_streamlines.png'); p.close()
if 'mesh' in which:
    L=open(D+'f117_full.su2').read().split('\n'); i=0
    while not L[i].startswith('NELEM'): i+=1
    ne=int(L[i].split('=')[1]); E=np.loadtxt(L[i+1:i+1+ne],dtype=np.int64)
    tets=E[E[:,0]==10][:,1:5]; i=i+1+ne
    while not L[i].startswith('NPOIN'): i+=1
    npn=int(L[i].split('=')[1].split()[0]); P=np.loadtxt(L[i+1:i+1+npn])[:,:3]
    g=pv.UnstructuredGrid({vtk.VTK_TETRA:tets},P)
    y=1.5
    sl=g.slice(normal=(0,1,0),origin=(0,y,0)).clip_box([-8.5,31.5,y-1,y+1,-9.5,8.5],invert=False)
    p=plotter(); p.add_mesh(sl,color='#26323f',show_edges=True,edge_color='#8ea2b5',line_width=0.6,lighting=False)
    p.add_mesh(s,color='#e07a3f',lighting=False)
    title(p,'F-117: the volume mesh, cut 1.5 m from the centre line','1.24 million tetrahedra: about 12 cm at the aircraft, growing to 8 m at the far-field boundary.')
    sc=np.array([11.5,y,1.0]); cam(p,sc+[0,-80,0],sc,up=(0,0,1),parallel=True); p.camera.parallel_scale=11
    p.screenshot(O+'f117_mesh.png')
    p.close()
print('done',sorted(os.listdir(O)))
