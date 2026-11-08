# 3D Mesh Subdivision Viewer (Loop & Modified Butterfly)

Egy interaktív, Python és PyVista alapú 3D geometriai megjelenítő és felületfinomító alkalmazás. A szoftver tetszőleges háromszögelt felülethálókat (`.obj`) olvas be, és billentyűvezérléssel valós idejű **Loop** (approximáló) és **Modified Butterfly** (interpoláló) subdivision (felosztási) iterációkat hajt végre rajtuk.

> **Fejlesztési megjegyzés:** A projekt a kurzus feladataként, önálló fejlesztésben készült a **Google Gemini AI** (Gemini 2.5 Pro / Flash) szakmai és algoritmikai közreműködésével.

---

## Főbb funkciók

- **Interaktív 3D megjelenítés:** Egérrel szabadon forgatható, zoomolható és mozgatható kamera (VTK / PyVista motor).
- **Két független subdivision séma:**
  - **Loop felosztás (Approximáló):** $C^2$ felületi folytonosságot eredményez reguláris környezetben, csökkenti a felület egyenetlenségeit, és természetes zsugorodási jelleget mutat.
  - **Modified Butterfly felosztás (Interpoláló):** Zorin–Schröder–Sweldens-féle 8 pontos lepke-maszk és extraordináris csúcsszabályok. Az eredeti csúcspontok koordinátái szigorúan változatlanok maradnak.
- **Dinamikus modellváltó:** Az `assets/` mappában elhelyezett tetszőleges `.obj` fájlok közötti azonnali váltás számbillentyűkkel, automatikus kameraközpontosítással (`reset_camera`).
- **Árnyalási módok közötti váltás:** Váltás a laponkénti árnyalás (**Flat Shading**) és a hálószerkezet (**Wireframe**) között egyetlen gombnyomással.
- **Topológiai tisztítás (Vertex Welding):** Automatikus duplikált pont összevonás és háromszögelés beolvasáskor, megelőzve a szakadásokat és a non-manifold hibákat.
- **Valós idejű telemetria:** Folyamatosan frissülő HUD a 3D nézetben (iterációszám, lapszám, csúcsszám), valamint futásidő-mérés a terminálban.

---

## Mappaszerkezet

```text
Subdivision/
│
├── assets/                  # 3D modellfájlok (.obj)
│   ├── cow.obj              # Tesztmodell (Low-poly tehén)
│   ├── icosphere.obj        # Ikozaéder gömbalap
│   └── cube.obj             # Háromszögelt kocka
│
├── algorithms/              # A geometriai felosztási sémák
│   ├── loop.py              # Loop subdivision algoritmus
│   └── butterfly.py         # Modified Butterfly subdivision algoritmus
│
├── viewer/                  # Megjelenítés és interakció
│   └── main.py              # PyVista plotter és vezérlési logika
│
└── README.md                # Dokumentáció
```

---

## Elméleti háttér és sémák

Mindkét séma $1 \rightarrow 4$ háromszögfelosztást alkalmaz (minden háromszöglap az élek felezésével 4 új rész-háromszögre bomlik), de a pontok pozicionálása alapvetően eltér:

### 1. Loop Séma (Approximáló)
- **Új élpontok:** A közös él két végpontja ($v_1, v_2$) $3/8$ súlyt, a két szomszédos háromszöglap szemközti csúcsai ($v_3, v_4$) $1/8$ súlyt kapnak:
  $$v_{új} = \frac{3}{8}(v_1 + v_2) + \frac{1}{8}(v_3 + v_4)$$
- **Régi csúcsok eltolása:** A régi $v$ csúcs pozíciója a saját értéke és a $k$ darab szomszédja ($v_i$) súlyozott átlaga:
  $$v'_{új} = (1 - k\beta)v + \beta \sum_{i=1}^k v_i$$
  ahol $\beta = \frac{1}{k}\left(\frac{5}{8} - \left(\frac{3}{8} + \frac{1}{4}\cos\frac{2\pi}{k}\right)^2\right)$.

### 2. Modified Butterfly Séma (Interpoláló)
- **Régi csúcsok:** Helyben maradnak ($v'_{új} = v$).
- **Új élpontok (Reguláris, $k=6$ eset):** 8 pontos maszk alapján:
  - Az él végpontjai: $1/2$ súly
  - Szemközti csúcsok: $1/8$ súly
  - Külső "szárny" csúcsok: $-1/16$ súly
- **Extraordináris eset ($k \ne 6$):** Zorin-féle korrekciós súlyok a csúcs körüli rendezett 1-gyűrű mentén, kiküszöbölve a felületi szingularitásokat és tüskeképződést.

---

## Telepítés és Futtatás

### 1. Előfeltételek
- Python 3.10, 3.11 vagy 3.12
- PyCharm vagy tetszőleges Python IDE

### 2. Virtuális környezet és csomagok telepítése
Nyiss egy terminált a projekt gyökerében:

```bash
# Függőségek telepítése
pip install pyvista numpy
```

*(Opcionális, ha nincs requirements.txt: `pip install pyvista numpy`)*

### 3. Futtatás
Indítsd el az alkalmazást a `viewer` könyvtárból:

```bash
python viewer/main.py
```

---

## Kezelési útmutató (Billentyűzet és Egér)

| Billentyű / Beviteli eszköz | Funkció |
| :--- | :--- |
| **`[L]`** | **Loop Subdivision** lépés végrehajtása az aktuális elemen |
| **`[B]`** | **Modified Butterfly Subdivision** lépés végrehajtása |
| **`[W]`** | **Flat Shading** $\leftrightarrow$ **Drótháló (Wireframe)** közötti átkapcsolás |
| **`[1]`, `[2]`, `[3]`, ...** | Modellváltás az `assets/` mappában lévő `.obj` fájlok között |
| **Egér bal gomb (nyomva tartva)** | 3D kamera forgatása az alakzat körül |
| **Egérgörgő** | Zoom (közelítés / távolítás) |
| **Egér jobb gomb / görgő lenyomva** | Kamera mozgatása (Pan) |

---

## Technológiai részletek

- **PyVista (VTK Backend):** Hardveresen gyorsított OpenGL megjelenítés, eseménykezelés és kamera pipeline.
- **NumPy:** Vektorizált koordinátaszámítások, él- és lapmátrixok kezelése.
- **Topológiai gráf:** Ad-hoc éllista és lap-összerendelés, amely hatékony szomszédsági bejárást biztosít Half-Edge struktúra memóriaterhelése nélkül.