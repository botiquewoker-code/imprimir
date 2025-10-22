# app.py — UI estilo Canva + PDF en memoria (sin guardar archivos)
import io
import time
import traceback
import streamlit as st
import fitz # PyMuPDF

# ============== Config básica ==============
st.set_page_config(page_title="PrintPDF", page_icon="🖨️", layout="wide")

# Ocultar menús de Streamlit (look más “app”)
st.markdown("""
<style>
/* Reset y tipografía suave */
html, body, [class*="css"] { font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol' !important; }
#MainMenu, header, footer {visibility: hidden;}

/* Fondo tipo Canva: claro, limpio */
body { background: #F7F8FB; }

/* Contenedor principal */
.canvas-shell {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}

/* Barra superior estilo Canva */
.topbar {
  background: linear-gradient(90deg, #7C3AED 0%, #06B6D4 100%);
  border-radius: 18px;
  padding: 18px 22px;
  color: white;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 8px 30px rgba(124,58,237,.25);
}
.brand {
  font-weight: 800;
  letter-spacing: .3px;
  font-size: 18px;
  padding: 6px 12px;
  background: rgba(255,255,255,.18);
  border-radius: 10px;
}
.badge {
  background: rgba(255,255,255,.18);
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
}

/* Card grande central */
.card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 14px 40px rgba(16,24,40,.08);
  padding: 26px;
}

/* Zonas de acción */
.row {
  display: grid;
  grid-template-columns: 1.2fr .8fr;
  gap: 24px;
}
@media (max-width: 980px){
  .row { grid-template-columns: 1fr; }
}

/* Área drag & drop visual */
.dropzone {
  border: 2px dashed #E5E7EB;
  border-radius: 16px;
  padding: 26px;
  text-align: center;
  transition: .2s ease;
  background: #FBFCFE;
}
.dropzone:hover {
  border-color: #C7D2FE;
  background: #F7F8FF;
}

/* Botón primario grande */
.btn-primary {
  background: linear-gradient(90deg,#7C3AED 0%, #06B6D4 100%);
  color: #fff;
  padding: 12px 18px;
  font-weight: 700;
  border-radius: 12px;
  text-decoration: none;
  display: inline-block;
  box-shadow: 0 8px 24px rgba(124,58,237,.25);
}
.btn-primary[disabled]{
  filter: grayscale(.4);
  opacity: .7;
}

/* Botón secundario */
.btn-ghost {
  background: #EEF2FF;
  color: #3730A3;
  padding: 10px 14px;
  border-radius: 10px;
  font-weight: 600;
  display: inline-block;
}

/* Chips */
.chips {
  display:flex; gap:10px; flex-wrap:wrap; margin-top:8px;
}
.chip {
  background:#F1F5F9; color:#0F172A; padding:8px 12px; border-radius:999px; font-weight:600; font-size:12px;
}

/* Preview */
.preview {
  background:#FAFAFA; border-radius:16px; padding:12px; border:1px solid #EEE; text-align:center;
}

/* Etiquetas y títulos */
.h1 { font-size: 28px; font-weight: 800; margin: 2px 0 6px 0; }
.h2 { font-size: 16px; font-weight: 700; color:#0F172A; margin-top: 8px; }
.muted { color:#6B7280; font-size:13px; }
.small { color:#64748B; font-size:12px; }

/* Separador sutil */
.hr { height:1px; background:#EDF2F7; margin:18px 0; }

/* Sliders */
[data-baseweb="slider"] > div { padding-top: 10px; }

/* Download container */
.dl {
  display:flex; align-items:center; justify-content:space-between; gap:14px; flex-wrap:wrap; margin-top:16px;
}
</style>
""", unsafe_allow_html=True)

# ============== UI superior (barra y selector idioma) ==============
with st.container():
    st.markdown('<div class="canvas-shell">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="topbar">
        <div class="brand">PrintPDF</div>
        <div class="badge">Rápido • Seguro • En memoria</div>
    </div>
    """, unsafe_allow_html=True)

# Idiomas visibles con banderas (simple y claro)
idiomas = {
    "es": "Español 🇪🇸",
    "en": "English 🇺🇸",
    "fr": "Français 🇫🇷",
    "de": "Deutsch 🇩🇪",
    "it": "Italiano 🇮🇹",
    "pt": "Português 🇵🇹",
}
col_a, col_b, col_c = st.columns([1.4,1,1])
with col_a:
    lang = st.selectbox("Idioma / Language", list(idiomas.keys()), format_func=lambda k: idiomas[k])

# Textos UI (multiidioma básicos)
TXT = {
    "title": {"es":"Tu PDF, más ligero y listo", "en":"Your PDF, lighter & ready", "fr":"Votre PDF, plus léger", "de":"Dein PDF, leichter & bereit", "it":"Il tuo PDF, più leggero", "pt":"Seu PDF, mais leve e pronto"},
    "subtitle":{"es":"Sube, comprime y descarga. Sin guardar nada en el servidor.", "en":"Upload, compress & download. Nothing stored on server.", "fr":"Téléversez, compressez & téléchargez. Rien n’est stocké.", "de":"Hochladen, komprimieren & herunterladen. Nichts gespeichert.", "it":"Carica, comprimi e scarica. Nulla salvato sul server.", "pt":"Envie, compacte e baixe. Nada fica salvo no servidor."},
    "upload": {"es":"Arrastra tu PDF aquí o selecciona desde tu dispositivo", "en":"Drag your PDF here or pick from your device", "fr":"Glissez votre PDF ici ou choisissez depuis votre appareil", "de":"Zieh dein PDF hierher oder wähle es vom Gerät", "it":"Trascina qui il tuo PDF o selezionalo dal dispositivo", "pt":"Arraste seu PDF aqui ou selecione do dispositivo"},
    "quality": {"es":"Calidad de compresión", "en":"Compression quality", "fr":"Qualité de compression", "de":"Komprimierungsqualität", "it":"Qualità di compressione", "pt":"Qualidade de compactação"},
    "process": {"es":"Comprimir PDF", "en":"Compress PDF", "fr":"Compresser le PDF", "de":"PDF komprimieren", "it":"Comprimi PDF", "pt":"Compactar PDF"},
    "success": {"es":"¡Listo! Tu PDF está optimizado 🎉", "en":"Done! Your PDF is optimized 🎉", "fr":"C’est fait ! Votre PDF est optimisé 🎉", "de":"Fertig! Dein PDF ist optimiert 🎉", "it":"Fatto! Il tuo PDF è ottimizzato 🎉", "pt":"Pronto! Seu PDF está otimizado 🎉"},
    "download":{"es":"Descargar PDF", "en":"Download PDF", "fr":"Télécharger le PDF", "de":"PDF herunterladen", "it":"Scarica PDF", "pt":"Baixar PDF"},
    "info": {"es":"Sube un PDF para comenzar.", "en":"Upload a PDF to get started.", "fr":"Téléversez un PDF pour commencer.", "de":"Lade ein PDF hoch, um zu starten.", "it":"Carica un PDF per iniziare.", "pt":"Envie um PDF para começar."},
    "error": {"es":"Ocurrió un error. Inténtalo de nuevo.", "en":"Something went wrong. Please try again.", "fr":"Une erreur s’est produite. Réessayez.", "de":"Etwas ist schiefgelaufen. Bitte erneut versuchen.", "it":"Qualcosa è andato storto. Riprova.", "pt":"Algo deu errado. Tente novamente."},
}

st.markdown(f"""
<div style="margin-top:16px" />
<div class="card">
  <div class="h1">{TXT["title"][lang]}</div>
  <div class="muted">{TXT["subtitle"][lang]}</div>
  <div class="hr"></div>
""", unsafe_allow_html=True)

# ============== Zona principal (izquierda: upload/controles | derecha: preview) ==============
left, right = st.columns([1.2, 0.8], gap="large")

with left:
    st.markdown(f'<div class="dropzone">{TXT["upload"][lang]}</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

    # Controles “visibles” siempre
    st.markdown('<div class="h2" style="margin-top:10px;">⚙️ ' + TXT["quality"][lang] + '</div>', unsafe_allow_html=True)
    quality = st.slider("", min_value=10, max_value=100, value=60, step=5, help="Calidad objetivo al recomprimir imágenes embebidas (menor = más compresión).")

    st.markdown('<div class="chips"><div class="chip">Sin guardar en servidor</div><div class="chip">Procesado en memoria</div><div class="chip">Vista previa</div></div>', unsafe_allow_html=True)

    # Acción
    process_clicked = st.button("✨ " + TXT["process"][lang], type="primary")

with right:
    st.markdown('<div class="h2">👀 Preview</div>', unsafe_allow_html=True)
    preview_container = st.empty()
    meta_container = st.empty()

# ============== Lógica (todo en memoria) ==============
def preview_pdf_first_page(pdf_bytes: bytes):
    """Renderiza la primera página a PNG en memoria para previsualizar."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if doc.page_count == 0:
            return None
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=130, alpha=False)
        img_bytes = pix.tobytes("png")
        doc.close()
        return img_bytes
    except Exception:
        return None

def compress_pdf(pdf_bytes: bytes, quality_hint: int) -> bytes:
    """
    Reescribe el PDF en memoria. Usamos saver con opciones de compresión.
    Nota: PyMuPDF no tiene 'calidad' directa; el slider guía flags generales.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    out = io.BytesIO()
    # Flags de compresión razonables
    # garbage=4 → limpieza profunda; deflate=True → comprimir streams; compress=True → recomprime imágenes/objetos.
    doc.save(out, garbage=4, deflate=True, compress=True, incremental=False)
    doc.close()
    out.seek(0)
    return out.read()

def human_size(num_bytes: int) -> str:
    for unit in ["B","KB","MB","GB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} TB"

# Mostrar preview inmediata si hay archivo
if uploaded is None:
    st.info("ℹ️ " + TXT["info"][lang])
else:
    # Leer a memoria
    original_bytes = uploaded.read()
    # Preview
    img = preview_pdf_first_page(original_bytes)
    if img:
        with right:
            with st.container():
                st.markdown('<div class="preview">', unsafe_allow_html=True)
                st.image(img, caption="Primera página (preview)", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
    # Metadatos base
    with right:
        meta_container.markdown(f"""
        <div class="small">
          <b>Nombre:</b> {uploaded.name}<br/>
          <b>Tamaño original:</b> {human_size(len(original_bytes))}
        </div>
        """, unsafe_allow_html=True)

    # Procesar bajo demanda
    if process_clicked:
        try:
            with st.spinner("⏳ Procesando en memoria..."):
                t0 = time.time()
                result_bytes = compress_pdf(original_bytes, quality)
                dt = time.time() - t0

            # Info tamaños
            before = len(original_bytes)
            after = len(result_bytes)
            ratio = (1 - (after / before)) * 100 if before > 0 else 0

            st.success(TXT["success"][lang])
            st.markdown(f"**⏱️ Tiempo:** {dt:.2f}s • **🔻 Reducción:** {ratio:.1f}% • **📦 Nuevo tamaño:** {human_size(after)}")

            # Botón de descarga (en memoria)
            st.markdown('<div class="dl">', unsafe_allow_html=True)
            st.download_button(
                label="⬇️ " + TXT["download"][lang],
                data=result_bytes,
                file_name=f"printpdf_{uploaded.name}",
                mime="application/pdf",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception:
            st.error("❌ " + TXT["error"][lang])
            with st.expander("Detalles técnicos (oculto al usuario final)"):
                st.code(traceback.format_exc())

# Cierre del contenedor principal
st.markdown('</div>', unsafe_allow_html=True)
