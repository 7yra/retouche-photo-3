import os
from PIL import Image, ImageEnhance

INPUT_DIR = "photos_a_traiter"
REF_IMAGE_PATH = "photos_reference/fond_2.png"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_image(input_path, ref_img):
img = Image.open(input_path).convert("RGBA")

```
# Ajustement léger luminosité / contraste
enhancer = ImageEnhance.Brightness(img)
img = enhancer.enhance(1.05)

enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(1.05)

# Redimensionnement pour correspondre au fond
img = img.resize(ref_img.size)

# Fusion simple (collage centré)
background = ref_img.copy()
background.paste(img, (0, 0), img)

return background
```

def main():
if not os.path.exists(REF_IMAGE_PATH):
raise Exception("Image de référence manquante")

```
ref_img = Image.open(REF_IMAGE_PATH).convert("RGBA")

files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]

if not files:
    raise Exception("Aucune image à traiter")

for filename in files:
    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    result = process_image(input_path, ref_img)
    result.convert("RGB").save(output_path, "JPEG")

    print(f"Traité: {filename}")
```

if **name** == "**main**":
main()

