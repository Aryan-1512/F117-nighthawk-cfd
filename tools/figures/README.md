# README figures

Renders the images in `images/` straight from the SU2 results and the mesh with PyVista (VTK, the engine ParaView is built on), so every figure can be regenerated.

```
pip install pyvista vtk numpy
python tools/figures/render_f117.py case/
```

Run it from the repository root after meshing and the simulation, so `case/` contains `f117_full.su2`, `flow.vtu` and `surface_flow.vtu`.
