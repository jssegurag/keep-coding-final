import os
from PIL import Image

TIFF_ROOT = os.path.join('src', 'resources', 'tiff')
PDF_ROOT = os.path.join('src', 'resources', 'docs')


def convert_tiff_to_pdf(tiff_path, pdf_path):
    """
    Convierte un archivo .tif (posiblemente multi-página) a .pdf usando Pillow.
    """
    try:
        with Image.open(tiff_path) as img:
            # Verificar si es multi-página
            if hasattr(img, 'n_frames') and img.n_frames > 1:
                print(f"📄 Archivo multi-página detectado: {tiff_path} ({img.n_frames} páginas)")
                
                # Lista para almacenar todas las páginas
                pages = []
                
                # Convertir cada página
                for i in range(img.n_frames):
                    img.seek(i)
                    # Convertir a RGB si es necesario
                    if img.mode in ("RGBA", "P"):
                        page = img.convert("RGB")
                    else:
                        page = img.copy()
                    pages.append(page)
                
                # Guardar todas las páginas como un solo PDF
                if pages:
                    pages[0].save(pdf_path, "PDF", resolution=100.0, save_all=True, append_images=pages[1:])
                    print(f"✅ Convertido: {tiff_path} -> {pdf_path} ({len(pages)} páginas)")
            else:
                # Archivo de una sola página
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(pdf_path, "PDF", resolution=100.0)
                print(f"✅ Convertido: {tiff_path} -> {pdf_path} (1 página)")
                
    except Exception as e:
        print(f"❌ Error al convertir {tiff_path}: {e}")

def main():
    for root, dirs, files in os.walk(TIFF_ROOT):
        for file in files:
            if file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                tiff_file = os.path.join(root, file)
                # Mantener la estructura de subcarpetas
                rel_path = os.path.relpath(root, TIFF_ROOT)
                output_dir = os.path.join(PDF_ROOT, rel_path)
                os.makedirs(output_dir, exist_ok=True)
                pdf_file = os.path.splitext(file)[0] + '.pdf'
                pdf_path = os.path.join(output_dir, pdf_file)
                convert_tiff_to_pdf(tiff_file, pdf_path)

if __name__ == "__main__":
    main() 