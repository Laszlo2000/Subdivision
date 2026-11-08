import os
import time
import numpy as np
import pyvista as pv

from algorithms.loop import loop_subdivision
from algorithms.butterfly import butterfly_subdivision


class MeshViewer:
    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir
        self.is_wireframe = False
        self.iteration = 0
        self.current_scheme = "Eredeti"
        self.current_model_name = ""

        # Elérhető OBJ fájlok betöltése
        self.models = [f for f in os.listdir(self.assets_dir) if f.lower().endswith('.obj')]
        if not self.models:
            raise FileNotFoundError(f"Nem található .obj fájl ebben a könyvtárban: {self.assets_dir}")

        # Plotter létrehozása
        self.plotter = pv.Plotter(window_size=[1080, 720])
        self.plotter.set_background('#1e1e1e')
        self.actor = None
        self.mesh = None

        # Alapértelmezett modell megnyitása
        default_model = 'cow.obj' if 'cow.obj' in self.models else self.models[0]
        self.load_model(default_model)

        # Billentyűesemények bekötése
        self.plotter.add_key_event('w', self.toggle_shading)
        self.plotter.add_key_event('W', self.toggle_shading)

        # Sémaválasztó billentyűk (L = Loop, B = Butterfly)
        self.plotter.add_key_event('l', lambda: self.step_subdivision('Loop'))
        self.plotter.add_key_event('L', lambda: self.step_subdivision('Loop'))
        self.plotter.add_key_event('b', lambda: self.step_subdivision('Butterfly'))
        self.plotter.add_key_event('B', lambda: self.step_subdivision('Butterfly'))

        # Számbillentyűk (1, 2, 3...) a modellek közötti váltáshoz
        for idx, filename in enumerate(self.models[:9]):
            key = str(idx + 1)
            self.plotter.add_key_event(key, lambda name=filename: self.load_model(name))

        self.update_ui_text()

    def update_ui_text(self):
        """Képernyő bal felső infó sávjának frissítése."""
        model_shortcuts = ", ".join([f"[{i + 1}] {m}" for i, m in enumerate(self.models[:4])])
        status = (
            f"=== SUBDIVISION VIEWER ===\n"
            f"Modell:    {self.current_model_name}\n"
            f"Séma:      {self.current_scheme}\n"
            f"Iteráció:  {self.iteration}\n"
            f"Csúcsok:   {self.mesh.n_points}\n"
            f"Lapok:     {self.mesh.n_cells}\n"
            f"Árnyalás:  {'Wireframe' if self.is_wireframe else 'Flat Shading'}\n\n"
            f"VEZÉRLÉS:\n"
            f"  [L]      Loop Subdivision futtatása\n"
            f"  [B]      Butterfly Subdivision futtatása\n"
            f"  [W]      Wireframe\n"
            f"  [S]      Flat Shading\n"
            f"  Modell:  {model_shortcuts}\n"
            f"  Egér:\n"
            f"  [LMB] Forgatás\n"
            f"  [RMB] Zoom (Görgető)"
        )
        self.plotter.add_text(
            status,
            position='upper_left',
            font_size=9,
            color='white',
            name='instructions'
        )

    def load_model(self, filename: str):
        """Modell újratöltése és állapot alaphelyzetbe állítása."""
        filepath = os.path.join(self.assets_dir, filename)
        raw_mesh = pv.read(filepath)

        # Duplikált csúcsok összevonása és háromszögelés
        welded = raw_mesh.clean(tolerance=1e-5, absolute=False)
        self.mesh = welded.triangulate()
        self.current_model_name = filename
        self.current_scheme = "Eredeti"
        self.iteration = 0

        if self.actor is not None:
            self.plotter.remove_actor(self.actor)

        self.actor = self.plotter.add_mesh(
            self.mesh,
            color='lightgray',
            style='wireframe' if self.is_wireframe else 'surface'
        )

        self.plotter.reset_camera()
        self.update_ui_text()
        self.plotter.render()
        print(f"\n[Modell betöltve] {filename} (Csúcsok: {self.mesh.n_points}, Lapok: {self.mesh.n_cells})")

    def toggle_shading(self):
        """Átkapcsolás Flat Shading és Wireframe között."""
        self.is_wireframe = not self.is_wireframe
        self.actor.prop.style = 'wireframe' if self.is_wireframe else 'surface'
        self.update_ui_text()
        self.plotter.render()

    def step_subdivision(self, scheme: str):
        """Kiválasztott subdivision séma futtatása méréssel."""
        prev_verts = self.mesh.n_points
        prev_faces = self.mesh.n_cells

        print(f"\n--- [{scheme} Iteráció #{self.iteration + 1} indul: {self.current_model_name}] ---")
        print(f"  Kezdeti állapot: {prev_verts} csúcs, {prev_faces} lap")

        start_time = time.time()

        raw_faces = self.mesh.faces.reshape(-1, 4)[:, 1:4]
        verts = self.mesh.points

        if scheme == 'Loop':
            new_verts, new_faces = loop_subdivision(verts, raw_faces)
        elif scheme == 'Butterfly':
            new_verts, new_faces = butterfly_subdivision(verts, raw_faces)
        else:
            return

        # PyVista PolyData újraépítése
        n_faces = len(new_faces)
        padding = np.full((n_faces, 1), 3, dtype=np.int64)
        pv_faces = np.hstack((padding, new_faces.astype(np.int64))).ravel()

        self.mesh = pv.PolyData(new_verts.astype(np.float32), pv_faces)
        self.iteration += 1
        self.current_scheme = scheme

        elapsed = time.time() - start_time
        print(f"  Új állapot:      {self.mesh.n_points} csúcs, {n_faces} lap")
        print(f"  Futási idő:      {elapsed:.3f} másodperc")

        self.plotter.remove_actor(self.actor)
        self.actor = self.plotter.add_mesh(
            self.mesh,
            color='lightgray',
            style='wireframe' if self.is_wireframe else 'surface'
        )

        self.update_ui_text()
        self.plotter.render()

    def run(self):
        self.plotter.show()


if __name__ == '__main__':
    # Helyes elérési út: viewer/ szülőkönyvtárából az assets/ mappa megkeresése
    assets_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
    app = MeshViewer(assets_folder)
    app.run()