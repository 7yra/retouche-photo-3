import os
from PIL import Image, ImageEnhance

INPUT_DIR = "photos_a_traiter"
REF_IMAGE_PATH = "photos_reference/fond_2.png"
OUTPUT_DIR = "output"


def find_subject_bbox(img):
    """
    Détection simple du sujet principal par différence avec la couleur du bord.
    Suppose que le fond de l'image source est relativement uniforme.
    Retourne une bounding box (left, top, right, bottom).
    """
    rgba = img.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size

    # Couleur moyenne approximative des coins
    corners = [
        px[0, 0],
        px[w - 1, 0],
        px[0, h - 1],
        px[w - 1, h - 1],
    ]

    avg = tuple(sum(c[i] for c in corners) // 4 for i in range(4))

    def is_background(c):
        # Tolérance simple
        return (
            abs(c[0] - avg[0]) < 35
            and abs(c[1] - avg[1]) < 35
            and abs(c[2] - avg[2]) < 35
        )

    xs = []
    ys = []

    for y in range(h):
        for x in range(w):
            c = px[x, y]
            if not is_background(c):
                xs.append(x)
                ys.append(y)

    if not xs or not ys:
        # fallback : toute l'image
        return (0, 0, w, h)

    left = max(min(xs) - 5, 0)
    top = max(min(ys) - 5, 0)
    right = min(max(xs) + 5, w)
    bottom = min(max(ys) + 5, h)

    return (left, top, right, bottom)


def crop_subject(img):
    bbox = find_subject_bbox(img)
    return img.crop(bbox)


def adjust_piece(piece):
    enhancer = ImageEnhance.Brightness(piece)
    piece = enhancer.enhance(1.03)

    enhancer = ImageEnhance.Contrast(piece)
    piece = enhancer.enhance(1.04)

    return piece


def fit_subject_to_reference(piece, ref_img):
    """
    Place la pièce au centre sur le fond de référence
    en gardant les proportions.
    """
    ref_w, ref_h = ref_img.size
    piece_w, piece_h = piece.size

    # On garde une marge pour éviter que la pièce touche les bords
    max_w = int(ref_w * 0.78)
    max_h = int(ref_h * 0.78)

    scale = min(max_w / piece_w, max_h / piece_h)
    new_w = max(1, int(piece_w * scale))
    new_h = max(1, int(piece_h * scale))

    piece_resized = piece.resize((new_w, new_h), Image.LANCZOS)

    x = (ref_w - new_w) // 2
    y = (ref_h - new_h) // 2

    return piece_resized, x, y


def process_image(input_path, ref_img):
    src = Image.open(input_path).convert("RGBA")
    ref = ref_img.convert("RGBA").copy()

    piece = crop_subject(src)
    piece = adjust_piece(piece)

    piece_resized, x, y = fit_subject_to_reference(piece, ref)

    # Si l'image source n'a pas de vraie transparence, on colle comme opaque
    ref.paste(piece_resized, (x, y), piece_resized)

    return ref


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(REF_IMAGE_PATH):
        raise FileNotFoundError("Image de référence manquante : photos_reference/fond_2.png")

    if not os.path.isdir(INPUT_DIR):
        raise FileNotFoundError("Dossier introuvable : photos_a_traiter")

    ref_img = Image.open(REF_IMAGE_PATH).convert("RGBA")

    files = [
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]

    if not files:
        raise RuntimeError("Aucune image à traiter dans photos_a_traiter")

    treated = []

    for filename in files:
        input_path = os.path.join(INPUT_DIR, filename)

        base, _ = os.path.splitext(filename)
        output_path = os.path.join(OUTPUT_DIR, f"{base}.jpg")

        result = process_image(input_path, ref_img)
        result.convert("RGB").save(output_path, "JPEG", quality=95)

        treated.append(output_path)
        print(f"Traité: {filename} -> {output_path}")

    print(f"Total traité: {len(treated)} image(s)")


if __name__ == "__main__":
    main()
