import os
import time
import pyvista as pv
import numpy as np
from algorithms.loop import loop_subdivision


class MeshViewer:
    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir
        self.is_wireframe = False
        self.iteration = 0
        self.current_model_name = ""

        # 1. Elérhető OBJ fájlok felderítése
        self.models = [f for f in os.listdir(self.assets_dir) if f.lower().endswith('.obj')]
        if not self.models:
            raise FileNotFoundError(f"Nem található .obj fájl ebben a mappában: {self.assets_dir}")

        # 2. Plotter inicializálása
        self.plotter = pv.Plotter(window_size=[1024, 768])
        self.plotter.set_background('#1e1e1e')
        self.actor = None
        self.mesh = None

        # 3. Első modell betöltése alapértelmezetten (pl. cow.obj ha van, vagy az első)
        default_model = 'cow.obj' if 'cow.obj' in self.models else self.models[0]
        self.load_model(default_model)

        # 4. Billentyűesemények bekötése
        self.plotter.add_key_event('w', self.toggle_shading)
        self.plotter.add_key_event('W', self.toggle_shading)
        self.plotter.add_key_event('space', self.step_subdivision)

        # Számbillentyűk (1, 2, 3...) hozzárendelése a modellekhez
        for idx, filename in enumerate(self.models[:9]):
            key = str(idx + 1)
            # Closure-kötés az adott fájlnévhez
            self.plotter.add_key_event(key, lambda name=filename: self.load_model(name))

        # 5. UI Információs szöveg frissítése
        self.update_ui_text()

    def update_ui_text(self):
        """A képernyő bal felső sarkában lévő HUD frissítése."""
        model_shortcuts = ", ".join([f"[{i+1}] {m}" for i, m in enumerate(self.models[:4])])
        status = (
            f"=== MESH INFORMÁCIÓK ===\n"
            f"Modell:    {self.current_model_name}\n"
            f"Iteráció:  {self.iteration}\n"
            f"Csúcsok:   {self.mesh.n_points}\n"
            f"Lapok:     {self.mesh.n_cells}\n"
            f"Árnyalás:  {'Wireframe' if self.is_wireframe else 'Flat Shading'}\n\n"
            f"VEZÉRLÉS:\n"
            f"  [Space]  Következő iteráció\n"
            f"  [W]      Wireframe\n"
            f"  [S]      Flat Shape\n"
            f"  Modell:  {model_shortcuts}\n"
            f"  Egér:\n"
            f"   Forgatás (LMB)\n"
            f"   Zoom (RMB)"
        )
        self.plotter.add_text(
            status,
            position='upper_left',
            font_size=9,
            color='white',
            name='instructions'
        )

    def load_model(self, filename: str):
        """Egy kiválasztott OBJ modell tiszta betöltése és resetelése."""
        filepath = os.path.join(self.assets_dir, filename)
        raw_mesh = pv.read(filepath)

        # Topológiai tisztítás és háromszögelés
        welded = raw_mesh.clean(tolerance=1e-5, absolute=False)
        self.mesh = welded.triangulate()
        self.current_model_name = filename
        self.iteration = 0

        # Megjelenítés cseréje
        if self.actor is not None:
            self.plotter.remove_actor(self.actor)

        self.actor = self.plotter.add_mesh(
            self.mesh,
            color='lightgray',
            style='wireframe' if self.is_wireframe else 'surface'
        )

        # Kamera újraszintezése az új objektum méretéhez
        self.plotter.reset_camera()
        self.update_ui_text()
        self.plotter.render()
        print(f"Modell betöltve: {filename} ({self.mesh.n_cells} lap)")

    def toggle_shading(self):
        """Átkapcsolás Flat Shading és Wireframe között."""
        self.is_wireframe = not self.is_wireframe
        self.actor.prop.style = 'wireframe' if self.is_wireframe else 'surface'
        self.plotter.render()

    def step_subdivision(self):
        """Iteráció futtatása méréssel és képernyő/terminál kiírással."""
        prev_verts_count = self.mesh.n_points
        prev_faces_count = self.mesh.n_cells

        print(f"\n[Iteráció #{self.iteration + 1} indul: {self.current_model_name}]")
        print(f"  Előző állapot:  {prev_verts_count} csúcs, {prev_faces_count} lap")

        start_time = time.time()

        # 1. Bemeneti lapok és csúcsok kinyerése
        raw_faces = self.mesh.faces.reshape(-1, 4)[:, 1:4]
        verts = self.mesh.points

        # 2. Loop felosztás
        new_verts, new_faces = loop_subdivision(verts, raw_faces)

        # 3. PyVista PolyData újraépítése
        n_faces = len(new_faces)
        padding = np.full((n_faces, 1), 3, dtype=np.int64)
        pv_faces = np.hstack((padding, new_faces.astype(np.int64))).ravel()

        self.mesh = pv.PolyData(new_verts.astype(np.float32), pv_faces)
        self.iteration += 1

        elapsed = time.time() - start_time

        # 4. Terminál naplózás
        print(f"  Új állapot:     {self.mesh.n_points} csúcs, {self.mesh.n_cells} lap")
        print(f"  Futási idő:     {elapsed:.3f} másodperc")

        # 5. Képernyő frissítése (Actor és Szöveg)
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
    # Az assets mappa elérési útja
    assets_folder = os.path.join(os.path.dirname(__file__), "..", 'assets')

    app = MeshViewer(assets_folder)
    app.run()