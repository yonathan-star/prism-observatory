#!/usr/bin/env python3
"""Measure exported STL geometry using only Python and NumPy.

This checks geometry, not rolling dynamics or print performance.
Run from any directory: python3 tools/verify_geometry.py
"""
from pathlib import Path
import hashlib
import json
import math
import re
import struct
import numpy as np

ROOT = Path(__file__).resolve().parents[1]



def load_stl(path):
    raw = path.read_bytes()
    count, = struct.unpack_from('<I', raw, 80)
    if len(raw) != 84 + 50 * count:
        raise ValueError(f'Invalid binary STL size: {path}')
    dtype = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)),
                      ('attribute', '<u2')])
    return np.frombuffer(raw, dtype=dtype, count=count, offset=84)['vertices'].astype(float)


def measure_mesh(path):
    tri = load_stl(path)
    vertices, inverse = np.unique(tri.reshape(-1, 3), axis=0, return_inverse=True)
    faces = inverse.reshape(-1, 3)
    edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    unoriented, edge_inverse, counts = np.unique(np.sort(edges, axis=1), axis=0,
                                                return_inverse=True, return_counts=True)
    orientation = np.where(edges[:, 0] < edges[:, 1], 1, -1)
    orientation_sum = np.bincount(edge_inverse, weights=orientation)
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    area2 = np.linalg.norm(normals, axis=1)
    signed_volume = np.einsum('ij,ij->i', tri[:, 0],
                              np.cross(tri[:, 1], tri[:, 2])).sum() / 6
    # Face connectivity via shared mesh edges, rather than just touching vertices.
    parent = np.arange(len(faces))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    edge_faces = np.tile(np.arange(len(faces)), 3)
    order = np.argsort(edge_inverse)
    offsets = np.concatenate([[0], np.cumsum(counts)])
    for k, n in enumerate(counts):
        if n == 2:
            f, g = edge_faces[order[offsets[k]:offsets[k + 1]]]
            a, b = find(f), find(g)
            if a != b:
                parent[a] = b
    components = len({find(i) for i in range(len(faces))})
    report = {
        'file': str(path.relative_to(ROOT)),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'triangles': len(tri), 'vertices': len(vertices), 'edges': len(unoriented),
        'bounds_mm': [vertices.min(axis=0).tolist(), vertices.max(axis=0).tolist()],
        'dimensions_mm': np.ptp(vertices, axis=0).tolist(),
        'signed_volume_mm3': float(signed_volume),
        'surface_area_mm2': float(area2.sum()/2),
        'boundary_edges': int(np.sum(counts == 1)),
        'nonmanifold_edges': int(np.sum(counts > 2)),
        'inconsistently_oriented_edges': int(np.count_nonzero(orientation_sum)),
        'degenerate_triangles': int(np.count_nonzero(area2 < 1e-9)),
        'connected_components': components,
    }
    report['passed'] = all([report['boundary_edges'] == 0,
                            report['nonmanifold_edges'] == 0,
                            report['inconsistently_oriented_edges'] == 0,
                            report['degenerate_triangles'] == 0,
                            components == 1, signed_volume > 0,
                            np.isfinite(tri).all()])
    return tri, report


def point_mesh_distance(point, tri):
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    ab, ac, ap = b-a, c-a, point-a
    aa = np.einsum('ij,ij->i', ab, ab)
    bb = np.einsum('ij,ij->i', ab, ac)
    cc = np.einsum('ij,ij->i', ac, ac)
    d = np.einsum('ij,ij->i', ap, ab)
    e = np.einsum('ij,ij->i', ap, ac)
    denom = aa*cc-bb*bb
    valid=np.abs(denom)>1e-18
    u=np.divide(d*cc-e*bb,denom,out=np.zeros_like(denom),where=valid)
    v=np.divide(e*aa-d*bb,denom,out=np.zeros_like(denom),where=valid)
    projection = a + u[:, None]*ab + v[:, None]*ac
    dsq = np.sum((point-projection)**2, axis=1)
    dsq[~valid | (u < 0) | (v < 0) | (u+v > 1)] = np.inf
    for start, end in [(a, b), (b, c), (c, a)]:
        edge = end-start
        edge2=np.einsum('ij,ij->i',edge,edge)
        t=np.clip(np.divide(np.einsum('ij,ij->i',point-start,edge),edge2,
                            out=np.zeros_like(edge2),where=edge2>1e-20),0,1)
        dsq = np.minimum(dsq, np.sum((point-start-t[:, None]*edge)**2, axis=1))
    return math.sqrt(float(dsq.min()))


def point_inside_mesh(point, tri):
    # Odd-even ray parity. A non-axis-aligned ray avoids regular grid edges;
    # coincident hit distances are deduplicated before counting crossings.
    direction = np.array([0.316227766, 0.777817459, 0.544331054])
    direction /= np.linalg.norm(direction)
    e1, e2 = tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]
    h = np.cross(direction, e2)
    det = np.einsum('ij,ij->i', e1, h)
    valid = np.abs(det) > 1e-10
    inv = np.divide(1., det, out=np.zeros_like(det), where=valid)
    s = point-tri[:, 0]
    u = inv*np.einsum('ij,ij->i', s, h)
    q = np.cross(s, e1)
    v = inv*(q @ direction)
    t = inv*np.einsum('ij,ij->i', e2, q)
    hit = valid & (u >= 0) & (v >= 0) & (u+v <= 1) & (t > 1e-7)
    return bool(len(np.unique(np.round(t[hit], 6))) % 2)

