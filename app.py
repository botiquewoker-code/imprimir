import io
import base64
from typing import List, Tuple

import streamlit as st
from PIL import Image, ImageOps
from PyPDF2 import PdfReader, PdfWriter
import fitz # PyMuPDF

# ==========================================
# CONFIGURACIÓN DE IDIOMAS Y TEXTOS
# ==========================================
LANGS = {
    "es": {
        "title": "🗂️ Conversor de Imágenes y Archivos",
        "about": "Convierte, comprime y gestiona imágenes y PDFs. Nada se guarda en el servidor; todo se procesa en memoria.",
        "pick_tool": "Elige una herramienta",
        "tools": {
            "img_convert": "Convertir imágenes entre formatos",
            "img_resize": "Redimensionar imagen",
            "img_compress": "Comprimir imagen (reducir peso)",
            "pdf_to_img": "PDF → Imágenes (una por página)",
            "pdf_merge": "Unir varios PDFs",
            "pdf_split": "Dividir PDF por rangos",
            "pdf_compress": "Comprimir PDF"
        },
        "upload_img": "Sube una imagen",
        "upload_imgs": "Sube una o varias imágenes",
        "upload_pdf": "Sube un PDF",
        "upload_pdfs": "Sube varios PDFs",
        "format": "Formato de salida",
        "quality": "Calidad",
        "width": "Ancho (px)",
        "height": "Alto (px)",
        "keep_ratio": "Mantener proporción",
        "convert": "Convertir",
        "download": "Descargar",
        "pages_range": "Rangos de páginas (p.ej. 1-3,6,8-9)",
        "compress": "Comprimir",
        "dpi": "DPI destino (recomendado 120-200)",
        "img_preview": "Vista previa",
        "ok": "Listo ✔️",
        "nothing": "Nada que procesar.",
        "pdf_quality_note": "Nota: la compresión re-muestrea imágenes internas y re-graba el PDF.",
    },
    "en": {
        "title": "🗂️ File & Image Toolkit",
        "about": "Convert, compress and manage images & PDFs. Nothing is stored; all processing happens in-memory.",
        "pick_tool": "Choose a tool",
        "tools": {
            "img_convert": "Convert images between formats",
            "img_resize": "Resize image",
            "img_compress": "Compress image (reduce size)",
            "pdf_to_img": "PDF → Images (one per page)",
            "pdf_merge": "Merge PDFs",
            "pdf_split": "Split PDF by ranges",
            "pdf_compress": "Compress PDF"
        },
        "upload_img": "Upload an image",
        "upload_imgs": "Upload one or more images",
        "upload_pdf": "Upload a PDF",
        "upload_pdfs": "Upload multiple PDFs",
        "format": "Output format",
        "quality": "Quality",
        "width": "Width (px)",
        "height": "Height (px)",
        "keep_ratio": "Keep aspect ratio",
        "convert": "Convert",
        "download": "Download",
        "pages_range": "Page ranges (e.g. 1-3,6,8-9)",
        "compress": "Compress",
        "dpi": "Target DPI (recommended 120-200)",
        "img_preview": "Preview",
        "ok": "Done ✔️",
        "nothing": "Nothing to process.",
        "pdf_quality_note": "Note: compression resamples inner images and rewrites the PDF.",
    },
}

FLAG = {
    "es": "🇪🇸 Español",
    "en": "🇬🇧 English",
}

st.set_page_config(page_title="Toolkit Archivos", page_icon="🗂️", layout="centered")

# Idioma
lang_key = st.sidebar.radio("🌍 Idioma / Language", list(FLAG.keys()), format_func=lambda k: FLAG[k], index=0)
T = LANGS[lang_key]

st.title(T["title"])
st.caption(T["about"])

# ==========================================
# FUNCIONES
# ==========================================

def pil_to_bytes(img: Image.Image, fmt: str, quality: int = 90) -> bytes:
    out = io.BytesIO()
    f = fmt.upper()
    params = {}
    if f in ("JPG", "JPEG"):
        f = "JPEG"
        params = {"quality": quality, "optimize": True}
    elif f == "PNG":
        params = {"optimize": True}
    elif f == "WEBP":
        params = {"quality": quality, "method": 6}
    img.save(out, format=f, **params)
    return out.getvalue()

def download_button_bytes(label: str, data: bytes, file_name: str, mime: str):
    st.download_button(label, data=data, file_name=file_name, mime=mime, use_container_width=True)
    st.session_state["processed"] = True

def parse_ranges(s: str, max_page: int) -> List[int]:
    pages = set()
    s = s.replace(" ", "")
    if not s:
        return []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-")
            for p in range(int(a), int(b) + 1):
                if 1 <= p <= max_page:
                    pages.add(p - 1)
        else:
            p = int(part)
            if 1 <= p <= max_page:
                pages.add(p - 1)
    return sorted(pages)

def pdf_merge(files: List[io.BytesIO]) -> bytes:
    writer = PdfWriter()
    for f in files:
        reader = PdfReader(f)
        for page in reader.pages:
            writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue()

def pdf_split(file: io.BytesIO, pages_0based: List[int]) -> bytes:
    reader = PdfReader(file)
    writer = PdfWriter()
    for p in pages_0based:
        if 0 <= p < len(reader.pages):
            writer.add_page(reader.pages[p])
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue()

def pdf_to_images(file: io.BytesIO, out_format: str = "PNG", dpi: int = 144) -> List[Tuple[str, bytes]]:
    out = []
    doc = fitz.open(stream=file.getvalue(), filetype="pdf")
    for i, page in enumerate(doc):
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_bytes = pil_to_bytes(img, out_format, quality=90)
        out.append((f"page_{i+1}.{out_format.lower()}", img_bytes))
    return out

def pdf_compress(file: io.BytesIO, dpi: int = 150, quality: int = 85) -> bytes:
    doc = fitz.open(stream=file.getvalue(), filetype="pdf")
    for page in doc:
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        page.clean_contents()
        img_b = pil_to_bytes(img, "JPEG", quality=quality)
        rect = page.rect
        page.insert_image(rect, stream=img_b)
    out = io.BytesIO()
    doc.save(out, deflate=True)
    out.seek(0)
    return out.getvalue()

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
tool_labels = T["tools"]
tool = st.sidebar.radio(
    f"🧰 {T['pick_tool']}",
    [
        "img_convert", "img_resize", "img_compress",
        "pdf_to_img", "pdf_merge", "pdf_split", "pdf_compress"
    ],
    format_func=lambda k: tool_labels[k]
)

if "processed" not in st.session_state:
    st.session_state["processed"] = False

# ==========================================
# FUNCIONES DE LA APP
# ==========================================

if tool == "img_convert":
    up = st.file_uploader(T["upload_imgs"], type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
    fmt = st.selectbox(T["format"], ["JPG", "PNG", "WEBP", "PDF"])
    quality = st.slider(f"{T['quality']} (JPG/WEBP)", 10, 100, 90)
    if st.button(T["convert"], use_container_width=True):
        if not up:
            st.warning(T["nothing"])
        else:
            if fmt == "PDF":
                images = [Image.open(f).convert("RGB") for f in up]
                buf = io.BytesIO()
                images[0].save(buf, format="PDF", save_all=True, append_images=images[1:])
                download_button_bytes(f"📄 {T['download']} PDF", buf.getvalue(), "images.pdf", "application/pdf")
            else:
                for f in up:
                    img = Image.open(f).convert("RGB")
                    data = pil_to_bytes(img, fmt, quality)
                    ext = fmt.lower() if fmt != "JPG" else "jpg"
                    download_button_bytes(f"⬇️ {T['download']} {f.name}.{ext}", data, f"{f.name.rsplit('.',1)[0]}.{ext}", f"image/{ext}")

elif tool == "pdf_merge":
    ups = st.file_uploader(T["upload_pdfs"], type=["pdf"], accept_multiple_files=True)
    if st.button(T["convert"], use_container_width=True):
        if not ups:
            st.warning(T["nothing"])
        else:
            data = pdf_merge([io.BytesIO(f.read()) for f in ups])
            download_button_bytes(f"⬇️ {T['download']} PDF", data, "merged.pdf", "application/pdf")

elif tool == "pdf_split":
    up = st.file_uploader(T["upload_pdf"], type=["pdf"])
    if up:
        reader = PdfReader(up)
        st.info(f"📄 {len(reader.pages)} páginas")
        up.seek(0)
    ranges = st.text_input(T["pages_range"], "1-3")
    if st.button(T["convert"], use_container_width=True):
        if not up:
            st.warning(T["nothing"])
        else:
            reader = PdfReader(up)
            pages = parse_ranges(ranges, len(reader.pages))
            if not pages:
                st.warning(T["nothing"])
            else:
                up.seek(0)
                data = pdf_split(up, pages)
                download_button_bytes(f"⬇️ {T['download']} PDF", data, "split.pdf", "application/pdf")

elif tool == "pdf_compress":
    st.caption(T["pdf_quality_note"])
    up = st.file_uploader(T["upload_pdf"], type=["pdf"])
    col1, col2 = st.columns(2)
    with col1:
        dpi = st.slider(T["dpi"], 72, 240, 150)
    with col2:
        q = st.slider(T["quality"], 10, 95, 85)
    if st.button(T["compress"], use_container_width=True):
        if not up:
            st.warning(T["nothing"])
        else:
            data = pdf_compress(up, dpi=dpi, quality=q)
            download_button_bytes(f"⬇️ {T['download']} PDF", data, "compressed.pdf", "application/pdf")

# ✅ Muestra "Listo" solo si hubo proceso
if "processed" in st.session_state and st.session_state["processed"]:
    st.success(T["ok"])

