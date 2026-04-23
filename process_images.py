import os
from PIL import Image, ImageEnhance

INPUT_DIR = "photos_a_traiter"
REF_IMAGE_PATH = "photos_reference/fond_2.png"
OUTPUT_DIR = "output"


def process_image(input_path, ref_img):
        img = Image.open(input_path).convert("RGBA")

        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)

        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.05)

        img = img.resize(ref_img.size)

        background = ref_img.copy()
        background.paste(img, (0, 0), img)

        return background


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(REF_IMAGE_PATH):
        raise Exception("Image de référence manquante")

    ref_img = Image.open(REF_IMAGE_PATH).convert("RGBA")

    files = [
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    if not files:
        raise Exception("Aucune image à traiter")

    for filename in files:
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)

        result = process_image(input_path, ref_img)
        result.convert("RGB").save(output_path, "JPEG")

        print(f"Traité: {filename}")


if __name__ == "__main__":
    main()
