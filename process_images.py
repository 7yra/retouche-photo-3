import os
from PIL import Image, ImageEnhance

INPUT_DIR = "photos_a_traiter"
REF_IMAGE_PATH = "photos_reference/fond_2.png"
OUTPUT_DIR = "output"

# Réglages prudents pour respecter au maximum la pièce d'origine
BRIGHTNESS_FACTOR = 1.02
CONTRAST_FACTOR = 1.03

# Taille max de la pièce par rapport à la référence
# Valeur prudente pour éviter les déformations visuelles
MAX_SUBJECT_WIDTH_RATIO = 0.72
MAX_SUBJECT_HEIGHT_RATIO = 0.72

# Tolérance de détection du fond
BACKGROUND_TOLERANCE = 28


def average_corner_color(img):
    px = img.load()
    w, h = img.size
    corners = [
        px[0, 0],
        px[w - 1, 0],
        px[0, h - 1],
        px[w - 1, h - 1],
    ]
    return tuple(sum(c[i] for c in corners) // 4 for i in range(4))


def is_background(pixel, bg):
    return (
        abs(pixel[0] - bg[0]) <= BACKGROUND_TOLERANCE
        and abs(pixel[1] - bg[1]) <= BACKGROUND_TOLERANCE
        and abs(pixel[2] - bg[2]) <= BACKGROUND_TOLERANCE
    )


def find_subject_bbox(img):
    """
    Détection prudente du sujet principal.
    On suppose que le fond source est plus uniforme que la pièce.
    """
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    bg = average_corner_color(img)

    xs = []
    ys = []

    for y in range(h):
        for x in range(w):
            pixel = px[x, y]
            if not is_background(pixel, bg):
                xs.append(x)
                ys.append(y)

    if not xs or not ys:
        return 0, 0, w, h

    margin = 4
    left = max(min(xs) - margin, 0)
    top = max(min(ys) - margin, 0)
    right = min(max(xs) + margin + 1, w)
    bottom = min(max(ys) + margin + 1, h)

    return left, top, right, bottom


def crop_subject(img):
    bbox = find_subject_bbox(img)
    return img.crop(bbox)


def adjust_piece(piece):
    """
    Ajustements très légers seulement.
    Pas de sharpening, pas de lissage, pas de suppression agressive.
    """
    enhancer = ImageEnhance.Brightness(piece)
    piece = enhancer.enhance(BRIGHTNESS_FACTOR)

    enhancer = ImageEnhance.Contrast(piece)
    piece = enhancer.enhance(CONTRAST_FACTOR)

    return piece


def fit_subject(piece, ref_img):
    """
    Garde strictement les proportions.
    Redimensionne la pièce sans la déformer.
    """
    ref_w, ref_h = ref_img.size
    pw, ph = piece.size

    max_w = int(ref_w * MAX_SUBJECT_WIDTH_RATIO)
    max_h = int(ref_h * MAX_SUBJECT_HEIGHT_RATIO)

    scale = min(max_w / pw, max_h / ph)
    new_w = max(1, int(pw * scale))
    new_h = max(1, int(ph * scale))

    resized = piece.resize((new_w, new_h), Image.LANCZOS)

    x = (ref_w - new_w) // 2
    y = (ref_h - new_h) // 2

    return resized, x, y


def ensure_square_reference(ref_img):
    """
    Si la référence n'est pas carrée, on la centre sur un fond carré
    en reprenant sa propre couleur moyenne de bord.
    """
    ref = ref_img.convert("RGBA")
    w, h = ref.size

    if w == h:
        return ref

    size = max(w, h)
    bg = average_corner_color(ref)
    square = Image.new("RGBA", (size, size), bg)

    x = (size - w) // 2
    y = (size - h) // 2
    square.paste(ref, (x, y), ref)

    return square


def compose_on_reference(piece, ref_img):
    """
    Colle la pièce sur le fond de référence sans changer son angle
    ni ses proportions.
    """
    base = ensure_square_reference(ref_img).copy()
    piece_resized, x, y = fit_subject(piece, base)
    base.paste(piece_resized, (x, y), piece_resized)
    return base


def process_image(input_path, ref_img):
    src = Image.open(input_path).convert("RGBA")

    # Extraction prudente du sujet
    piece = crop_subject(src)

    # Ajustements légers
    piece = adjust_piece(piece)

    # Composition finale
    result = compose_on_reference(piece, ref_img)

    return result


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
        name, _ = os.path.splitext(filename)
        output_path = os.path.join(OUTPUT_DIR, f"{name}.jpg")

        result = process_image(input_path, ref_img)
        result.convert("RGB").save(output_path, "JPEG", quality=95)

        treated.append(output_path)
        print(f"Traité: {filename} -> {output_path}")

    print(f"Total traité: {len(treated)} image(s)")


if __name__ == "__main__":
    main()
