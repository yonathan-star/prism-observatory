#!/usr/bin/env python3
"""Orthographic CPU renders of the actual exported STL triangle meshes.

No image generation, desktop, display, or OpenGL is used. NumPy + Pillow only.
"""
from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from mesh_math import ROOT, load_stl

BG = (18, 29, 39)
INK = (25, 55, 53)
MUTED = (88, 110, 105)
TEAL = np.array([40, 143, 133], dtype=float)
BASE = np.array([194, 212, 204], dtype=float)
GOLD = np.array([246, 177, 64], dtype=float)
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')


def font(size, bold=False):
    return ImageFont.truetype(str(FONT_DIR / ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')), size)


def render(tri, colors, size=(1500, 1050), direction=(1, -1.15, 1.65),
           target=None, scale=None, margin=45):
    w, h = size
    toward = np.array(direction, dtype=float)
    toward /= np.linalg.norm(toward)
    right = np.cross([0, 0, 1], toward)
    if np.linalg.norm(right) < 1e-9:
        right = np.array([1., 0, 0])
    right /= np.linalg.norm(right)
    up = np.cross(toward, right)
    basis = np.array([right, up, toward]).T
    projected = tri @ basis
    if target is None:
        low, high = projected.reshape(-1, 3).min(0), projected.reshape(-1, 3).max(0)
        center = (low+high)/2
        if scale is None:
            scale = min((w-2*margin)/(high[0]-low[0]), (h-2*margin)/(high[1]-low[1]))
    else:
        center = np.array(target) @ basis
    pixels = np.empty((h, w, 3), dtype=np.uint8)
    pixels[:] = BG
    zbuf = np.full((h, w), -np.inf, dtype=np.float32)
    xy = projected[:, :, :2].copy()
    xy[:, :, 0] = (xy[:, :, 0]-center[0])*scale+w/2
    xy[:, :, 1] = -(xy[:, :, 1]-center[1])*scale+h/2
    normals = np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-20)
    light = np.array([-0.5, -0.7, 1.7])
    light /= np.linalg.norm(light)
    shade = 0.42+0.52*np.maximum(normals @ light, 0)+0.06*np.maximum(normals[:, 2], 0)
    face_colors = np.clip(colors*shade[:, None], 0, 255).astype(np.uint8)
    for i, p in enumerate(xy):
        xmin, xmax = max(0, int(math.floor(p[:, 0].min()))), min(w-1, int(math.ceil(p[:, 0].max())))
        ymin, ymax = max(0, int(math.floor(p[:, 1].min()))), min(h-1, int(math.ceil(p[:, 1].max())))
        if xmin > xmax or ymin > ymax:
            continue
        a, b, c = p
        den = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den) < 1e-8:
            continue
        yy, xx = np.mgrid[ymin:ymax+1, xmin:xmax+1]
        xx, yy = xx+0.5, yy+0.5
        u = ((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        v = ((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
        q = 1-u-v
        depth = u*projected[i, 0, 2]+v*projected[i, 1, 2]+q*projected[i, 2, 2]
        old = zbuf[ymin:ymax+1, xmin:xmax+1]
        mask = (u >= -1e-8) & (v >= -1e-8) & (q >= -1e-8) & (depth > old)
        old[mask] = depth[mask]
        pixels[ymin:ymax+1, xmin:xmax+1][mask] = face_colors[i]

    def project_world(p):
        out = np.array(p) @ basis
        return ((out[0]-center[0])*scale+w/2, -(out[1]-center[1])*scale+h/2)

    return Image.fromarray(pixels), project_world


def arrow(draw, start, end, fill=INK, width=4):
    draw.line([start, end], fill=fill, width=width)
    d = np.array(end)-np.array(start)
    d = d/np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    tip = np.array(end)
    draw.polygon([tuple(tip), tuple(tip-13*d+5*n), tuple(tip-13*d-5*n)], fill=fill)

