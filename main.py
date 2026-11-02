import os
import pyvista as pv


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
        """Helyőrző az újabb iteráció indítására billentyűre."""
        self.iteration += 1
        print(f"Iteráció kiváltva (Space lenyomva) -> Lépés: {self.iteration}")

    def run(self):
        self.plotter.show()


if __name__ == '__main__':
    # Elérési út feloldása a projekt gyökeréhez képest
    model_path = os.path.join(os.path.dirname(__file__), 'assets', 'cup.obj')

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"A modellfájl nem található ezen az útvonalon: {model_path}")

    # OBJ betöltése
    loaded_mesh = pv.read(model_path)

    # Kötelező háromszögelés (biztosítja, hogy ne legyenek quad/ngon lapok)
    triangulated_mesh = loaded_mesh.triangulate()

    print(f"Modell betöltve: {triangulated_mesh.n_points} csúcspont, {triangulated_mesh.n_cells} lap")

    app = MeshViewer(triangulated_mesh)
    app.run()