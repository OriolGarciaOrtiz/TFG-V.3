import os
from PIL import Image

# 📂 Ruta base de tu dataset
BASE_DIR = "C:\\Users\\usuario\\Desktop\\YOLOv8Dataset\\images"

# Factor de reducción (ejemplo: 3 → reduce a 1/3 del tamaño original)
FACTOR = 3

def redimensionar_imagenes(carpeta):
    for archivo in os.listdir(carpeta):
        if archivo.lower().endswith((".jpg", ".jpeg", ".png")):
            ruta = os.path.join(carpeta, archivo)
            try:
                with Image.open(ruta) as img:
                    ancho, alto = img.size
                    nuevo_ancho = max(1, ancho // FACTOR)
                    nuevo_alto = max(1, alto // FACTOR)

                    # Redimensionar proporcionalmente
                    img = img.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)

                    # Sobrescribir optimizado en JPEG
                    img.save(ruta, format="JPEG", quality=85, optimize=True)
                    print(f"✅ Redimensionada: {archivo} ({ancho}x{alto} → {nuevo_ancho}x{nuevo_alto})")
            except Exception as e:
                print(f"❌ Error con {archivo}: {e}")

# Ejecutar en train y val
for split in ["train", "val"]:
    carpeta_split = os.path.join(BASE_DIR, split)
    redimensionar_imagenes(carpeta_split)

print("✨ Proceso terminado. Todas las imágenes han sido reducidas.")
