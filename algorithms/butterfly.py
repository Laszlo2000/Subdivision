import numpy as np


def get_weights_for_extraordinary(k: int):
    """Zorin-féle súlyok extraordináris csúcs esetén (Figure 4.5.b)."""
    if k == 3:
        s = np.array([5.0 / 12.0, -1.0 / 12.0, -1.0 / 12.0])
        c = 1.0 - np.sum(s)
        return c, s
    elif k == 4:
        s = np.array([3.0 / 8.0, 0.0, -1.0 / 8.0, 0.0])
        c = 1.0 - np.sum(s)
        return c, s
    else:
        i = np.arange(k)
        s = (1.0 / k) * (0.25 + np.cos(2.0 * np.pi * i / k) + 0.5 * np.cos(4.0 * np.pi * i / k))
        c = 1.0 - np.sum(s)
        return c, s


def get_ordered_ring_around_vertex(v_center, v_start, vertex_faces, faces, k_expected):
    """
    A v_center körüli 1-gyűrű szomszédjainak szigorúan folytonos sorbarendezése
    a háromszöglapok élein keresztül lépdelve.
    """
    ring = [v_start]
    curr_v = v_start
    prev_face = None

    for _ in range(k_expected - 1):
        found = False
        # Megkeressük azt a lapot, ami tartalmazza v_center-t és curr_v-t
        for f_idx in vertex_faces[v_center]:
            if f_idx == prev_face:
                continue
            face = faces[f_idx]
            if curr_v in face:
                # A lap harmadik csúcsa a következő szomszéd
                next_candidates = [v for v in face if v != v_center and v != curr_v]
                if next_candidates:
                    next_v = next_candidates[0]
                    if next_v not in ring:
                        ring.append(next_v)
                        prev_face = f_idx
                        curr_v = next_v
                        found = True
                        break
        if not found:
            break

    return ring if len(ring) == k_expected else None


def butterfly_subdivision(vertices: np.ndarray, faces: np.ndarray):
    n_verts = len(vertices)

    # 1. Topológia és lap-hozzárendelések
    edge_dict = {}
    vertex_neighbors = [set() for _ in range(n_verts)]
    vertex_faces = [[] for _ in range(n_verts)]

    for f_idx, face in enumerate(faces):
        for i in range(3):
            v1, v2 = face[i], face[(i + 1) % 3]
            v_opp = face[(i + 2) % 3]

            vertex_neighbors[v1].add(v2)
            vertex_neighbors[v2].add(v1)
            vertex_faces[v1].append(f_idx)

            edge = (min(v1, v2), max(v1, v2))
            if edge not in edge_dict:
                edge_dict[edge] = []
            edge_dict[edge].append(v_opp)

    # 2. Új pontok generálása
    edge_to_new_vertex_idx = {}
    new_edge_vertices = []

    for edge, opp_verts in edge_dict.items():
        v1, v2 = edge[0], edge[1]
        p1, p2 = vertices[v1], vertices[v2]

        # Határél
        if len(opp_verts) != 2:
            new_pt = 0.5 * (p1 + p2)
            idx = n_verts + len(new_edge_vertices)
            edge_to_new_vertex_idx[edge] = idx
            new_edge_vertices.append(new_pt)
            continue

        k1 = len(vertex_neighbors[v1])
        k2 = len(vertex_neighbors[v2])
        p3, p4 = vertices[opp_verts[0]], vertices[opp_verts[1]]

        # A) Mindkét csúcs reguláris (k == 6): 8 pontos lepke
        if k1 == 6 and k2 == 6:
            v3, v4 = opp_verts[0], opp_verts[1]
            wings = []
            for va, vb in [(v1, v3), (v1, v4), (v2, v3), (v2, v4)]:
                e = (min(va, vb), max(va, vb))
                if e in edge_dict:
                    for cand in edge_dict[e]:
                        if cand not in (v1, v2, v3, v4):
                            wings.append(cand)

            if len(wings) == 4:
                pw = np.sum(vertices[wings], axis=0)
                new_pt = 0.5 * (p1 + p2) + 0.125 * (p3 + p4) - 0.0625 * pw
            else:
                new_pt = 0.5 * (p1 + p2) + 0.125 * (p3 + p4)

        # B) Extraordináris esetek
        else:
            candidates = []
            for v_ext, v_other, k_val in [(v1, v2, k1), (v2, v1, k2)]:
                if k_val != 6:
                    c_center, s_weights = get_weights_for_extraordinary(k_val)
                    ordered_ring = get_ordered_ring_around_vertex(v_ext, v_other, vertex_faces, faces, k_val)

                    if ordered_ring is not None:
                        nb_pts = vertices[ordered_ring]
                        pt_ext = c_center * vertices[v_ext] + np.sum(s_weights[:, np.newaxis] * nb_pts, axis=0)
                        candidates.append(pt_ext)

            if len(candidates) == 2:
                new_pt = 0.5 * (candidates[0] + candidates[1])
            elif len(candidates) == 1:
                new_pt = candidates[0]
            else:
                # Ha a gyűrű nem záródik rendezetten, kiesik a tüske veszélye
                new_pt = 0.5 * (p1 + p2) + 0.125 * (p3 + p4)

        idx = n_verts + len(new_edge_vertices)
        edge_to_new_vertex_idx[edge] = idx
        new_edge_vertices.append(new_pt)

    # 3. Új háló összeállítása
    all_new_vertices = np.vstack((vertices, np.array(new_edge_vertices)))

    new_faces = []
    for face in faces:
        v0, v1, v2 = face[0], face[1], face[2]
        e01 = edge_to_new_vertex_idx[(min(v0, v1), max(v0, v1))]
        e12 = edge_to_new_vertex_idx[(min(v1, v2), max(v1, v2))]
        e20 = edge_to_new_vertex_idx[(min(v2, v0), max(v2, v0))]

        new_faces.append([v0, e01, e20])
        new_faces.append([v1, e12, e01])
        new_faces.append([v2, e20, e12])
        new_faces.append([e01, e12, e20])

    return all_new_vertices, np.array(new_faces)