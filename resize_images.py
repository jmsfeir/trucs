#!/usr/bin/env python3
"""
Redimensionne toutes les images du repo en copies réduites, destinées à
l'analyse visuelle par le modèle. Les copies sont placées dans un dossier
miroir `_resized/` à la racine, en conservant l'arborescence d'origine.

Objectif : réduire fortement le poids (base64) envoyé au modèle pour éviter
l'erreur "Improperly formed request" liée à la taille du contexte.
"""
import glob
import os
from PIL import Image, ImageOps

SRC_ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.path.join(SRC_ROOT, "_resized")

# Côté le plus long cible (px). 1400 reste lisible pour les titres de DVD/livres.
MAX_LONG_SIDE = 1400
# Qualité JPEG de sortie
JPEG_QUALITY = 80

EXTS = ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG")


def iter_images():
    for ext in EXTS:
        for f in glob.glob(os.path.join(SRC_ROOT, "**", ext), recursive=True):
            # Ignorer .git, le dossier de sortie, et tout dossier technique
            rel = os.path.relpath(f, SRC_ROOT)
            if rel.startswith(".git") or rel.startswith("_resized"):
                continue
            yield f, rel


def main():
    total = 0
    saved_in = 0
    saved_out = 0
    for src, rel in sorted(iter_images()):
        dst = os.path.join(OUT_ROOT, rel)
        # Normaliser l'extension de sortie en .jpg
        dst = os.path.splitext(dst)[0] + ".jpg"
        os.makedirs(os.path.dirname(dst), exist_ok=True)

        im = Image.open(src)
        # Respecter l'orientation EXIF puis convertir en RGB
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")

        w, h = im.size
        scale = MAX_LONG_SIDE / max(w, h)
        if scale < 1:
            new_size = (round(w * scale), round(h * scale))
            im = im.resize(new_size, Image.LANCZOS)

        im.save(dst, "JPEG", quality=JPEG_QUALITY, optimize=True)

        in_sz = os.path.getsize(src)
        out_sz = os.path.getsize(dst)
        saved_in += in_sz
        saved_out += out_sz
        total += 1

    print(f"{total} images redimensionnées")
    print(f"Poids total original : {saved_in/1e6:.1f} MB")
    print(f"Poids total réduit    : {saved_out/1e6:.1f} MB  "
          f"({saved_out/saved_in*100:.0f}% de l'original)")
    print(f"Copies dans : {OUT_ROOT}")


if __name__ == "__main__":
    main()
