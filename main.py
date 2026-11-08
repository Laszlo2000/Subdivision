import os
import pyvista as pv
from algorithms.loop import loop_subdivision
import numpy as np


class MeshViewer:
    def __init__(self, initial_mesh: pv.PolyData):
        self.mesh = initial_mesh
        self.is_wireframe = False
        self.iteration = 0

        # Plotter inicializálása
        self.plotter = pv.Plotter(window_size=[1024, 768])
        self.plotter.set_background('#1e1e1e')

        # Háló megjelenítése flat shadinggel
        self.actor = self.plotter.add_mesh(
            self.mesh,
            color='lightgray',
            show_edges=False,
            style='surface'
        )

        # PyVista/VTK beépített 'w' lefoglalásának felülbírálása
        # Kis- és nagybetűs leütést is regisztrálunk (Caps Lock esetére)
        self.plotter.add_key_event('W', self.toggle_shading)
        self.plotter.add_key_event('S', self.toggle_shading)
        self.plotter.add_key_event('space', self.step_subdivision)

        # Kezelési útmutató feliratozása
        self.plotter.add_text(
            "Felület váltó:\n [W] Wireframe  \n [S] Flat \n[Space] Új iteráció\nEgér:\n Bal gomb = Forgatás"
            "\n Jobb gomb = Zoom \nGörgetés = Zoom",
            position='upper_left',
            font_size=10,
            color='white'
        )

    def toggle_shading(self):
        """Megbízható átkapcsolás Flat Shading és Drótháló (Wireframe) között."""
        self.is_wireframe = not self.is_wireframe

        # A PyVista Actor Property stílusának közvetlen átállítása
        if self.is_wireframe:
            self.actor.prop.style = 'wireframe'
        else:
            self.actor.prop.style = 'surface'

        self.plotter.render()
        print(f"Megjelenítés mód: {'Wireframe' if self.is_wireframe else 'Flat Surface'}")

    def step_subdivision(self):
        """Újabb Loop subdivision iteráció futtatása a Space leütésekor."""
        self.iteration += 1
        print(f"--- Loop Iteráció #{self.iteration} indul ---")

        # 1. Pontok és lapok kinyerése a PyVista hálóból
        # A PyVista a lapokat [3, id1, id2, id3, 3, id4, ...] formában tárolja (VTK padding)
        # Ebből tiszta (M, 3) tömböt csinálunk:
        raw_faces = self.mesh.faces.reshape(-1, 4)[:, 1:4]
        verts = self.mesh.points

        # 2. Loop felosztás futtatása
        new_verts, new_faces = loop_subdivision(verts, raw_faces)

        # 3. Visszaalakítás PyVista PolyData formátumra
        padding = np.full((len(new_faces), 1), 3, dtype=np.int64)
        pv_faces = np.hstack((padding, new_faces)).ravel()

        # 4. Megjelenítés frissítése a Plotterben
        self.mesh = pv.PolyData(new_verts, pv_faces)
        self.plotter.clear_actors()
        self.actor = self.plotter.add_mesh(
            self.mesh,
            color='lightgray',
            style='wireframe' if self.is_wireframe else 'surface'
        )
        self.plotter.render()
        print(f"Befejezve: {len(new_verts)} csúcs, {len(new_faces)} lap.")

    def run(self):
        self.plotter.show()


if __name__ == '__main__':
    # Elérési út feloldása a projekt gyökeréhez képest
    model_path = os.path.join(os.path.dirname(__file__), 'assets', 'cow.obj')

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"A modellfájl nem található ezen az útvonalon: {model_path}")

    # OBJ betöltése
    loaded_mesh = pv.read(model_path)

    # Kötelező háromszögelés (biztosítja, hogy ne legyenek quad/ngon lapok)
    triangulated_mesh = loaded_mesh.triangulate()

    print(f"Modell betöltve: {triangulated_mesh.n_points} csúcspont, {triangulated_mesh.n_cells} lap")

    app = MeshViewer(triangulated_mesh)
    app.run()