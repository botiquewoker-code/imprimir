import streamlit as st
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import io
import fitz # PyMuPDF

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Imprimir - Conversor Universal", layout="wide")

# --- IDIOMAS (inicial) ---
IDIOMAS = {
    "es": {"titulo": "🖨️ Conversor de Imágenes y PDF", "boton": "Convertir", "descargar": "Descargar archivo"},
    "en": {"titulo": "🖨️ Image & PDF Converter", "boton": "Convert", "descargar": "Download file"},
    "fr": {"titulo": "🖨️ Convertisseur d’images et PDF", "boton": "Convertir", "descargar": "Télécharger"},
    "de": {"titulo": "🖨️ Bild- und PDF-Konverter", "boton": "Konvertieren", "descargar": "Herunterladen"},
    "ar": {"titulo": "🖨️ محول الصور وملفات PDF", "boton": "تحويل", "descargar": "تحميل الملف"}
}

# --- SELECCIÓN DE IDIOMA ---
lang = st.sidebar.selectbox("🌐 Idioma / Language", list(IDIOMAS.keys()))
txt = IDIOMAS[lang]

st.title(txt["titulo"])
st.write("Convierte imágenes a PDF o reduce tamaño de archivos directamente en tu navegador.")

# --- SUBIDA DE ARCHIVOS ---
uploaded_file = st.file_uploader("📂 Sube tu imagen o archivo PDF", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    file_name = uploaded_file.name.lower()
    if st.button(txt["boton"]):
        if file_name.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            output = io.BytesIO()
            writer.write(output)
            st.success("✅ PDF procesado correctamente.")
            st.download_button(txt["descargar"], output.getvalue(), file_name="archivo.pdf")
        else:
            image = Image.open(uploaded_file)
            output = io.BytesIO()
            image.save(output, format="PDF")
            st.success("✅ Imagen convertida correctamente.")
            st.download_button(txt["descargar"], output.getvalue(), file_name="imagen.pdf")
