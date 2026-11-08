import os
import pyvista as pv

assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(assets_dir, exist_ok=True)

# 1. Alacsony felbontású ikozaéder (szép szimmetrikus gömb-alap) - 20 lap
ico = pv.Icosphere(radius=1.0, nsub=0).triangulate()
ico.save(os.path.join(assets_dir, 'icosphere.obj'))

# 2. Háromszögelt kocka - 12 lap
cube = pv.Cube().triangulate()
cube.save(os.path.join(assets_dir, 'cube.obj'))

# 3. Low-poly tehén (klasszikus CG tesztmodell, ~5800 lap helyett 1000-re vágva)
cow = pv.examples.download_cow().triangulate().decimate(0.8)
cow.save(os.path.join(assets_dir, 'cow.obj'))

print("Teszthálók elmentve az assets mappába!")