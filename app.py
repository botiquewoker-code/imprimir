# app.py
import io, os, zipfile, base64
from datetime import datetime

import streamlit as st
from PIL import Image, ImageOps
from PyPDF2 import PdfReader, PdfWriter
import fitz # PyMuPDF (para PDF avanzado)

# ---- opcionales: si no están instalados, se ocultan las pestañas ----
try:
    from pydub import AudioSegment # requiere ffmpeg en el sistema
    HAS_AUDIO = True
except Exception:
    HAS_AUDIO = False

try:
    from moviepy.editor import VideoFileClip # requiere ffmpeg
    HAS_VIDEO = True
except Exception:
    HAS_VIDEO = False

# =========================
# CONFIG & TRADUCCIONES
# =========================
st.set_page_config(page_title="Omni Tools", page_icon="🧰", layout="wide")

LANGS = {
    "es": {"flag":"🇪🇸","name":"Español"},
    "en": {"flag":"🇬🇧","name":"English"},
    "fr": {"flag":"🇫🇷","name":"Français"},
    "de": {"flag":"🇩🇪","name":"Deutsch"},
    "it": {"flag":"🇮🇹","name":"Italiano"},
    "pt": {"flag":"🇵🇹","name":"Português"},
    "ar": {"flag":"🇸🇦","name":"العربية"},
    "tr": {"flag":"🇹🇷","name":"Türkçe"},
    "pl": {"flag":"🇵🇱","name":"Polski"},
    "nl": {"flag":"🇳🇱","name":"Nederlands"},
    "sv": {"flag":"🇸🇪","name":"Svenska"},
    "no": {"flag":"🇳🇴","name":"Norsk"},
    "da": {"flag":"🇩🇰","name":"Dansk"},
    "fi": {"flag":"🇫🇮","name":"Suomi"},
    "ru": {"flag":"🇷🇺","name":"Русский"},
    "hi": {"flag":"🇮🇳","name":"हिन्दी"},
    "zh": {"flag":"🇨🇳","name":"中文"},
    "ja": {"flag":"🇯🇵","name":"日本語"},
    "ko": {"flag":"🇰🇷","name":"한국어"},
}

# textos por idioma
TXT = {
    "title": {
        "es":"🧰 Herramientas de Archivos Todo-en-Uno",
        "en":"🧰 All-in-One File Tools",
        "fr":"🧰 Outils Fichiers Tout-en-Un",
        "de":"🧰 Datei-Werkzeuge All-in-One",
        "it":"🧰 Strumenti File All-in-One",
        "pt":"🧰 Ferramentas de Arquivos Tudo-em-Um",
        "ar":"🧰 أدوات ملفات شاملة",
        "tr":"🧰 Hepsi Bir Arada Dosya Araçları",
        "pl":"🧰 Wszechstronne narzędzia plików",
        "nl":"🧰 Alles-in-één Bestands­tools",
        "sv":"🧰 Allt-i-ett filverktyg",
        "no":"🧰 Alt-i-ett filverktøy",
        "da":"🧰 Alt-i-én filværktøjer",
        "fi":"🧰 Kaikki yhdessä -tiedostotyökalut",
        "ru":"🧰 Набор инструментов для файлов",
        "hi":"🧰 ऑल-इन-वन फ़ाइल टूल्स",
        "zh":"🧰 全能文件工具",
        "ja":"🧰 すべて入りファイルツール",
        "ko":"🧰 올인원 파일 도구",
    },
    "sidebar_lang": {
        "es":"🌐 Idioma",
        "en":"🌐 Language",
        "fr":"🌐 Langue",
        "de":"🌐 Sprache",
        "it":"🌐 Lingua",
        "pt":"🌐 Idioma",
        "ar":"🌐 اللغة",
        "tr":"🌐 Dil",
        "pl":"🌐 Język",
        "nl":"🌐 Taal",
        "sv":"🌐 Språk",
        "no":"🌐 Språk",
        "da":"🌐 Sprog",
        "fi":"🌐 Kieli",
        "ru":"🌐 Язык",
        "hi":"🌐 भाषा",
        "zh":"🌐 语言",
        "ja":"🌐 言語",
        "ko":"🌐 언어",
    },
    "tabs": {
        "images":{
            "es":"🖼️ Imágenes",
            "en":"🖼️ Images",
            "fr":"🖼️ Images",
            "de":"🖼️ Bilder",
            "it":"🖼️ Immagini",
            "pt":"🖼️ Imagens",
            "ar":"🖼️ صور",
            "tr":"🖼️ Görseller",
            "pl":"🖼️ Obrazy",
            "nl":"🖼️ Afbeeldingen",
            "sv":"🖼️ Bilder",
            "no":"🖼️ Bilder",
            "da":"🖼️ Billeder",
            "fi":"🖼️ Kuvat",
            "ru":"🖼️ Изображения",
            "hi":"🖼️ चित्र",
            "zh":"🖼️ 图片",
            "ja":"🖼️ 画像",
            "ko":"🖼️ 이미지",
        },
        "pdf":{
            "es":"📄 PDF",
            "en":"📄 PDF",
            "fr":"📄 PDF",
            "de":"📄 PDF",
            "it":"📄 PDF",
            "pt":"📄 PDF",
            "ar":"📄 PDF",
            "tr":"📄 PDF",
            "pl":"📄 PDF",
            "nl":"📄 PDF",
            "sv":"📄 PDF",
            "no":"📄 PDF",
            "da":"📄 PDF",
            "fi":"📄 PDF",
            "ru":"📄 PDF",
            "hi":"📄 PDF",
            "zh":"📄 PDF",
            "ja":"📄 PDF",
            "ko":"📄 PDF",
        },
        "text":{
            "es":"📝 Texto",
            "en":"📝 Text",
            "fr":"📝 Texte",
            "de":"📝 Text",
            "it":"📝 Testo",
            "pt":"📝 Texto",
            "ar":"📝 نص",
            "tr":"📝 Metin",
            "pl":"📝 Tekst",
            "nl":"📝 Tekst",
            "sv":"📝 Text",
            "no":"📝 Tekst",
            "da":"📝 Tekst",
            "fi":"📝 Teksti",
            "ru":"📝 Текст",
            "hi":"📝 पाठ",
            "zh":"📝 文本",
            "ja":"📝 テキスト",
            "ko":"📝 텍스트",
        },
        "zip":{
            "es":"🗜️ ZIP",
            "en":"🗜️ ZIP",
            "fr":"🗜️ ZIP",
            "de":"🗜️ ZIP",
            "it":"🗜️ ZIP",
            "pt":"🗜️ ZIP",
            "ar":"🗜️ ZIP",
            "tr":"🗜️ ZIP",
            "pl":"🗜️ ZIP",
            "nl":"🗜️ ZIP",
            "sv":"🗜️ ZIP",
            "no":"🗜️ ZIP",
            "da":"🗜️ ZIP",
            "fi":"🗜️ ZIP",
            "ru":"🗜️ ZIP",
            "hi":"🗜️ ZIP",
            "zh":"🗜️ ZIP",
            "ja":"🗜️ ZIP",
            "ko":"🗜️ ZIP",
        },
        "audio":{
            "es":"🎵 Audio",
            "en":"🎵 Audio",
            "fr":"🎵 Audio",
            "de":"🎵 Audio",
            "it":"🎵 Audio",
            "pt":"🎵 Áudio",
            "ar":"🎵 صوت",
            "tr":"🎵 Ses",
        },
        "video":{
            "es":"🎬 Vídeo",
            "en":"🎬 Video",
            "fr":"🎬 Vidéo",
            "de":"🎬 Video",
            "it":"🎬 Video",
            "pt":"🎬 Vídeo",
            "ar":"🎬 فيديو",
            "tr":"🎬 Video",
        },
    },
    "ui": {
        "upload_imgs":{
            "es":"Sube imágenes (JPG/PNG/WebP) — múltiples",
            "en":"Upload images (JPG/PNG/WebP) — multiple",
            "fr":"Importez des images (JPG/PNG/WebP) — multiple",
            "de":"Bilder hochladen (JPG/PNG/WebP) — mehrere",
            "it":"Carica immagini (JPG/PNG/WebP) — multiple",
            "pt":"Envie imagens (JPG/PNG/WebP) — múltiplas",
            "ar":"حمّل صور (JPG/PNG/WebP) — متعدد",
            "tr":"Görseller yükleyin (JPG/PNG/WebP) — çoklu",
        },
        "quality":{
            "es":"Calidad (JPEG/WebP)",
            "en":"Quality (JPEG/WebP)",
            "fr":"Qualité (JPEG/WebP)",
            "de":"Qualität (JPEG/WebP)",
            "it":"Qualità (JPEG/WebP)",
            "pt":"Qualidade (JPEG/WebP)",
            "ar":"الجودة (JPEG/WebP)",
            "tr":"Kalite (JPEG/WebP)",
        },
        "maxw":{
            "es":"Ancho máximo (px) — 0 = original",
            "en":"Max width (px) — 0 = original",
            "fr":"Largeur max (px) — 0 = original",
            "de":"Max. Breite (px) — 0 = original",
            "it":"Larghezza max (px) — 0 = originale",
            "pt":"Largura máx (px) — 0 = original",
        },
        "format":{
            "es":"Formato de salida",
            "en":"Output format",
            "fr":"Format de sortie",
            "de":"Ausgabeformat",
            "it":"Formato di output",
            "pt":"Formato de saída",
        },
        "convert":{
            "es":"Convertir / Comprimir",
            "en":"Convert / Compress",
            "fr":"Convertir / Compresser",
            "de":"Konvertieren / Komprimieren",
            "it":"Converti / Comprimi",
            "pt":"Converter / Comprimir",
            "ar":"تحويل / ضغط",
            "tr":"Dönüştür / Sıkıştır",
        },
        "download_zip":{
            "es":"Descargar ZIP",
            "en":"Download ZIP",
            "fr":"Télécharger ZIP",
            "de":"ZIP herunterladen",
            "it":"Scarica ZIP",
            "pt":"Baixar ZIP",
            "ar":"تحميل ملف ZIP",
            "tr":"ZIP indir",
        },
        "upload_pdf":{
            "es":"Sube PDF(s)",
            "en":"Upload PDF(s)",
            "fr":"Importez PDF",
            "de":"PDF(s) hochladen",
            "it":"Carica PDF",
            "pt":"Envie PDF(s)",
        },
        "pdf_action":{
            "es":"Acción PDF",
            "en":"PDF Action",
            "fr":"Action PDF",
            "de":"PDF-Aktion",
            "it":"Azione PDF",
            "pt":"Ação PDF",
        },
        "merge":"Merge/Merge/Assemblern/Unire/Unir",
        "compress":{
            "es":"Comprimir (bajar imágenes a 120 DPI)",
            "en":"Compress (downscale images to 120 DPI)",
        },
        "extract_text":{
            "es":"Extraer texto",
            "en":"Extract text",
            "fr":"Extraire le texte",
            "de":"Text extrahieren",
            "it":"Estrai testo",
            "pt":"Extrair texto",
        },
        "process":{
            "es":"Procesar",
            "en":"Process",
            "fr":"Traiter",
            "de":"Verarbeiten",
            "it":"Elabora",
            "pt":"Processar",
            "ar":"تنفيذ",
            "tr":"İşle",
        },
        "download": {
    "es": "Descargar",
    "en": "Download",
    "fr": "Télécharger",
    "de": "Herunterladen",
    "it": "Scarica",
    "pt": "Baixar",
},

"text_area": {
    "es": "Pega o escribe tu texto...",
    "en": "Paste or type your text...",
},

"ops": {
    "es": "Operación",
    "en": "Operation",
},

import io
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image

        "text_area":{
            "es":"Pega o escribe tu texto…",
            "en":"Paste or type your text…",
        },
        "ops":{
            "es":"Operación",
            "en":"Operation",
        },
        "to_upper":{"es":"MAYÚSCULAS","en":"UPPERCASE"},
        "to_lower":{"es":"minúsculas","en":"lowercase"},
        "replace":{"es":"Buscar/Reemplazar","en":"Find/Replace"},
        "from":{"es":"Buscar","en":"Find"},
        "to":{"es":"Reemplazar por","en":"Replace with"},
        "make_zip":{
            "es":"Crear ZIP",
            "en":"Create ZIP",
        },
        "unzip":{
            "es":"Descomprimir ZIP",
            "en":"Unzip ZIP",
        },
        "upload_files":{
            "es":"Sube archivos",
            "en":"Upload files",
        },
        "ready":{
            "es":"✅ Listo. Descarga abajo.",
            "en":"✅ Ready. Download below.",
        },
        "not_available":{
            "es":"No disponible en este servidor.",
            "en":"Not available on this server.",
        }
    }
}

def t(key, lang):
    # key puede ser "title" o "ui.upload_imgs" etc.
    parts = key.split(".")
    node = TXT
    for p in parts[:-1]:
        node = node[p]
    leaf = parts[-1]
    entry = node.get(leaf, {})
    if isinstance(entry, dict):
        return entry.get(lang, entry.get("en", leaf))
    return entry

# =========================
# SIDEBAR / LENGUAJE
# =========================
lang_options = [f'{LANGS[k]["flag"]} {LANGS[k]["name"]} ({k})' for k in LANGS]
default_index = list(LANGS.keys()).index("es") if "es" in LANGS else 0
chosen = st.sidebar.selectbox(t("sidebar_lang", "es"), lang_options, index=default_index)
current_lang = chosen.split("(")[-1].replace(")","").strip()

st.title(t("title", current_lang))

st.caption("⚡ Todo en tu navegador. Nada se almacena en el servidor.")

# =========================
# TABS (secciones)
# =========================
tabs_labels = [
    t("tabs.images", current_lang),
    t("tabs.pdf", current_lang),
    t("tabs.text", current_lang),
    t("tabs.zip", current_lang),
]

if HAS_AUDIO:
    tabs_labels.append(t("tabs.audio", current_lang))
if HAS_VIDEO:
    tabs_labels.append(t("tabs.video", current_lang))

tabs = st.tabs(tabs_labels)

# ------------- IMÁGENES -------------
with tabs[0]:
    st.subheader(t("tabs.images", current_lang))
    files = st.file_uploader(t("ui.upload_imgs", current_lang), type=["jpg","jpeg","png","webp"], accept_multiple_files=True)
    col1,col2,col3 = st.columns(3)
    with col1:
        quality = st.slider(t("ui.quality", current_lang), 30, 100, 80, 5)
    with col2:
        max_w = st.number_input(t("ui.maxw", current_lang), min_value=0, value=0, step=100)
    with col3:
        out_fmt = st.selectbox(t("ui.format", current_lang), ["JPEG","WEBP","PNG","PDF"], index=0)

    if st.button(t("ui.convert", current_lang), type="primary", use_container_width=True, key="img_convert"):
        if not files:
            st.warning("Sube al menos una imagen.")
        else:
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as z:
                for f in files:
                    img = Image.open(f).convert("RGB")
                    if max_w and img.width > max_w:
                        ratio = max_w / img.width
                        new_size = (max_w, max(1, int(img.height*ratio)))
                        img = img.resize(new_size, Image.LANCZOS)

                    out_io = io.BytesIO()
                    if out_fmt == "PDF":
                        img.save(out_io, format="PDF")
                        ext = "pdf"
                    else:
                        img.save(out_io, format=out_fmt, quality=quality, optimize=True)
                        ext = out_fmt.lower()
                    out_io.seek(0)
                    base = os.path.splitext(f.name)[0]
                    z.writestr(f"{base}.{ext}", out_io.read())

            zip_buf.seek(0)
            st.success(t("ui.ready", current_lang))
            st.download_button(t("ui.download_zip", current_lang), data=zip_buf, file_name=f"images_{datetime.now().strftime('%Y%m%d_%H%M')}.zip", mime="application/zip", use_container_width=True)

# ------------- PDF -------------
with tabs[1]:
    st.subheader("📄 PDF")
    pdfs = st.file_uploader(t("ui.upload_pdf", current_lang), type=["pdf"], accept_multiple_files=True)
    action = st.selectbox(t("ui.pdf_action", current_lang), [t("merge","en").split("/")[0], t("ui.compress", current_lang), t("ui.extract_text", current_lang)])

    if st.button(t("ui.process", current_lang), type="primary", use_container_width=True, key="pdf_process"):
        if not pdfs:
            st.warning("Sube al menos un PDF.")
        else:
            if action == t("merge","en").split("/")[0]:
                writer = PdfWriter()
                for f in pdfs:
                    r = PdfReader(f)
                    for p in r.pages:
                        writer.add_page(p)
                out = io.BytesIO()
                writer.write(out)
                out.seek(0)
                st.success(t("ui.ready", current_lang))
                st.download_button(t("ui.download", current_lang)+" PDF", data=out, file_name="merged.pdf", mime="application/pdf", use_container_width=True)

            elif action == t("ui.compress", current_lang):
                # compresión via PyMuPDF: rasterizar imágenes a 120 DPI aprox
                result = io.BytesIO()
                with fitz.open(stream=pdfs[0].read(), filetype="pdf") as doc:
                    new_doc = fitz.open()
                    for page in doc:
                        pix = page.get_pixmap(dpi=120) # reducir
                        img_pdf = fitz.open("pdf", fitz.Image(pix).pdf)
                        new_doc.insert_pdf(img_pdf)
                    new_doc.save(result)
                result.seek(0)
                st.success(t("ui.ready", current_lang))
                st.download_button(t("ui.download", current_lang)+" PDF", data=result, file_name="compressed.pdf", mime="application/pdf", use_container_width=True)

            else: # extract text
                out_txt = io.StringIO()
                for f in pdfs:
                    f.seek(0)
                    with fitz.open(stream=f.read(), filetype="pdf") as doc:
                        for page in doc:
                            out_txt.write(page.get_text())
                            out_txt.write("\n")
                b = out_txt.getvalue().encode("utf-8")
                st.success(t("ui.ready", current_lang))
                st.download_button(t("ui.download", current_lang)+" .txt", data=b, file_name="extracted.txt", mime="text/plain", use_container_width=True)

# ------------- TEXTO -------------
with tabs[2]:
    st.subheader(t("tabs.text", current_lang))
    text_in = st.text_area(t("ui.text_area", current_lang), height=180)
    op = st.selectbox(t("ui.ops", current_lang), [t("to_upper", current_lang), t("to_lower", current_lang), t("replace", current_lang)])

    colA,colB = st.columns(2)
    repl_from = repl_to = ""
    if op == t("replace", current_lang):
        with colA:
            repl_from = st.text_input(t("ui.from", current_lang))
        with colB:
            repl_to = st.text_input(t("ui.to", current_lang))

    if st.button(t("ui.process", current_lang), type="primary", use_container_width=True, key="text_btn"):
        if not text_in.strip():
            st.warning("Escribe o pega texto.")
        else:
            if op == t("to_upper", current_lang):
                out = text_in.upper()
            elif op == t("to_lower", current_lang):
                out = text_in.lower()
            else:
                out = text_in.replace(repl_from, repl_to)
            st.success(t("ui.ready", current_lang))
            st.code(out, language="text")
            st.download_button(t("ui.download", current_lang)+" .txt", data=out.encode("utf-8"), file_name="text.txt", mime="text/plain", use_container_width=True)

# ------------- ZIP -------------
with tabs[3]:
    st.subheader("🗜️ ZIP")
    mode = st.radio("", [t("ui.make_zip", current_lang), t("ui.unzip", current_lang)], horizontal=True)

    if mode == t("ui.make_zip", current_lang):
        up = st.file_uploader(t("ui.upload_files", current_lang), accept_multiple_files=True)
        if st.button(t("ui.process", current_lang), type="primary", use_container_width=True, key="zip_make"):
            if not up:
                st.warning("Sube archivos.")
            else:
                zbuf = io.BytesIO()
                with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
                    for f in up:
                        z.writestr(f.name, f.read())
                zbuf.seek(0)
                st.success(t("ui.ready", current_lang))
                st.download_button(t("ui.download", current_lang)+" ZIP", data=zbuf, file_name="files.zip", mime="application/zip", use_container_width=True)
    else:
        z = st.file_uploader("ZIP", type=["zip"])
        if st.button(t("ui.process", current_lang), type="primary", use_container_width=True, key="zip_un"):
            if not z:
                st.warning("Sube un ZIP.")
            else:
                with zipfile.ZipFile(io.BytesIO(z.read())) as zip_ref:
                    names = zip_ref.namelist()
                    st.success(f"{t('ui.ready', current_lang)}")
                    for n in names:
                        data = zip_ref.read(n)
                        st.download_button(f"⬇️ {n}", data=data, file_name=n, use_container_width=True)

# ------------- AUDIO (opcional) -------------
if HAS_AUDIO:
    with tabs[4]:
        st.subheader(t("tabs.audio", current_lang))
        st.caption("Convertir a MP3 (requiere ffmpeg en el servidor).")
        upa = st.file_uploader("Audio", type=["wav","mp3","ogg","m4a"])
        if st.button(t("ui.process", current_lang), type="primary", use_container_width=True, key="audio_btn"):
            if not upa:
                st.warning("Sube un archivo de audio.")
            else:
                try:
                    raw = io.BytesIO(upa.read())
                    raw.seek(0)
                    audio = AudioSegment.from_file(raw)
                    out_io = io.BytesIO()
                    audio.export(out_io, format="mp3", bitrate="192k")
                    out_io.seek(0)
                    st.success(t("ui.ready", current_lang))
                    st.download_button(t("ui.download", current_lang)+" MP3", data=out_io, file_name="audio.mp3", mime="audio/mpeg", use_container_width=True)
                except Exception:
                    st.error(t("ui.not_available", current_lang))

# ---------
import streamlit as st

# Ocultar el menú y el pie de página de Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# --- Optimización del rendimiento ---
import streamlit as st

@st.cache_data
def procesar_archivo(archivo):
    # Procesar archivos solo en memoria (sin guardarlos en disco)
    file_bytes = archivo.read()
    file_stream = io.BytesIO(file_bytes)
    return file_stream



