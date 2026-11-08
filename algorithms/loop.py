import numpy as np


def compute_beta(k: int) -> float:
    """A Loop séma eredeti súlyozó tényezője (Figure 4.3 alapján)."""
    return (1.0 / k) * (5.0 / 8.0 - (3.0 / 8.0 + 0.25 * np.cos(2.0 * np.pi / k)) ** 2)


def loop_subdivision(vertices: np.ndarray, faces: np.ndarray):
    """
    Egy Loop subdivision iteráció végrehajtása.

    :param vertices: (N, 3) méretű float numpy tömb a pontok koordinátáival.
    :param faces: (M, 3) méretű int numpy tömb a háromszöglapok csúcsindexeivel.
    :return: (new_vertices, new_faces)
    """
    n_verts = len(vertices)

    # 1. Élek és szomszédságok feltérképezése
    # edge_dict kulcsa: (min_idx, max_idx) rendezett csúcspár
    # értéke: lista a szomszédos lapokról és a szemközti csúcsokról: [(face_idx, opp_vertex), ...]
    edge_dict = {}
    vertex_neighbors = [set() for _ in range(n_verts)]

    for f_idx, face in enumerate(faces):
        for i in range(3):
            v1, v2 = face[i], face[(i + 1) % 3]
            v_opp = face[(i + 2) % 3]

            # Gráf szomszédság feljegyzése
            vertex_neighbors[v1].add(v2)
            vertex_neighbors[v2].add(v1)

            edge = (min(v1, v2), max(v1, v2))
            if edge not in edge_dict:
                edge_dict[edge] = []
            edge_dict[edge].append(v_opp)

    # 2. Új élpontok (Edge points) generálása
    edge_to_new_vertex_idx = {}
    new_edge_vertices = []

    for edge, opp_verts in edge_dict.items():
        v1, v2 = edge[0], edge[1]
        p1, p2 = vertices[v1], vertices[v2]

        if len(opp_verts) == 2:
            # Belső él: 3/8 * (p1 + p2) + 1/8 * (p3 + p4)
            p3, p4 = vertices[opp_verts[0]], vertices[opp_verts[1]]
            new_pt = 0.375 * (p1 + p2) + 0.125 * (p3 + p4)
        else:
            # Határél: sima felezőpont 1/2 * (p1 + p2)
            new_pt = 0.5 * (p1 + p2)

        idx = n_verts + len(new_edge_vertices)
        edge_to_new_vertex_idx[edge] = idx
        new_edge_vertices.append(new_pt)

    # 3. Régi csúcspontok áthelyezése (Even vertices frissítése)
    updated_old_vertices = np.zeros_like(vertices)
    for i in range(n_verts):
        neighbors = list(vertex_neighbors[i])
        k = len(neighbors)

        # Ellenőrizzük, hogy határcsúcs-e (van-e olyan éle, amihez csak 1 lap tartozik)
        boundary_neighbors = []
        for nb in neighbors:
            edge = (min(i, nb), max(i, nb))
            if len(edge_dict[edge]) == 1:
                boundary_neighbors.append(nb)

        if len(boundary_neighbors) == 2:
            # Határcsúcs: 3/4 * v + 1/8 * (v_left + v_right)
            p_nb = vertices[boundary_neighbors]
            updated_old_vertices[i] = 0.75 * vertices[i] + 0.125 * np.sum(p_nb, axis=0)
        else:
            # Belső csúcs: (1 - k*beta) * v + beta * szumma(v_szomszédok)
            beta = compute_beta(k)
            sum_neighbors = np.sum(vertices[neighbors], axis=0)
            updated_old_vertices[i] = (1.0 - k * beta) * vertices[i] + beta * sum_neighbors

    # Új csúcshalmaz összeállítása
    if len(new_edge_vertices) > 0:
        all_new_vertices = np.vstack((updated_old_vertices, np.array(new_edge_vertices)))
    else:
        all_new_vertices = updated_old_vertices

    # 4. Új háromszöglapok definiálása (1 lapból 4 lap)
    new_faces = []
    for face in faces:
        v0, v1, v2 = face[0], face[1], face[2]

        e01 = edge_to_new_vertex_idx[(min(v0, v1), max(v0, v1))]
        e12 = edge_to_new_vertex_idx[(min(v1, v2), max(v1, v2))]
        e20 = edge_to_new_vertex_idx[(min(v2, v0), max(v2, v0))]

        # A négy új részháromszög azonos körüljárási iránnyal (CCW)
        new_faces.append([v0, e01, e20])
        new_faces.append([v1, e12, e01])
        new_faces.append([v2, e20, e12])
        new_faces.append([e01, e12, e20])

    return all_new_vertices, np.array(new_faces)