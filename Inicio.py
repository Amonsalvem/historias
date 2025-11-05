import os
import base64
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from openai import OpenAI

# ============================
# Helpers
# ============================
def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def get_api_key() -> str:
    # Prioridad: Secrets → input
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    return st.session_state.get("typed_key", "")

# ============================
# Estado
# ============================
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "full_response" not in st.session_state:
    st.session_state.full_response = ""
if "base64_image" not in st.session_state:
    st.session_state.base64_image = ""
if "typed_key" not in st.session_state:
    st.session_state.typed_key = ""

# ============================
# Page / Theme
# ============================
st.set_page_config(page_title="Tablero Místico", layout="wide", initial_sidebar_state="collapsed")

# CSS dark minimal (negro/blanco)
st.markdown("""
<style>
:root { --bg: #000000; --fg: #ffffff; --muted:#bdbdbd; --card:#0a0a0a; --border:#1f1f1f;}
html, body, [data-testid="stAppViewContainer"] { background: var(--bg) !important; color: var(--fg) !important; }
h1,h2,h3,h4,h5,h6, p, label, span, div, code { color: var(--fg) !important; }
[data-testid="stSidebar"] { background: var(--bg) !important; border-left: 1px solid var(--border); }
[data-baseweb="select"] > div, .stTextInput>div>div>input, textarea, .stTextArea textarea,
.stColorPicker, .stSlider, .stFileUploader, .stCheckbox, .stTextInput>div>div,
.stButton>button { color: var(--fg) !important; }
.stTextInput>div>div>input, textarea, .stTextArea textarea {
    background:#0b0b0b !important; border:1px solid var(--border) !important; border-radius:12px; }
.stButton>button {
    background: transparent !important; color: var(--fg) !important;
    border:1px solid var(--fg) !important; border-radius:999px !important;
    padding:0.6rem 1.2rem; transition: all .2s ease;
}
.stButton>button:hover { transform: translateY(-1px); box-shadow: 0 0 0 2px #ffffff22 inset; }
.block-card {
    background: var(--card); border:1px solid var(--border); border-radius:18px; padding:18px;
}
hr { border-color: var(--border) !important; }
.small { color: var(--muted) !important; font-size:0.9rem; }
.center { display:flex; align-items:center; justify-content:center; }
.kicker { letter-spacing:.08em; text-transform:uppercase; font-size:.75rem; color:var(--muted); }
</style>
""", unsafe_allow_html=True)

# ============================
# Header
# ============================
st.markdown('<div class="kicker">Oráculo Digital</div>', unsafe_allow_html=True)
st.markdown("<h1>꩜ Tablero Místico de Predicciones ꩜</h1>", unsafe_allow_html=True)
st.caption("Dibuja sobre el lienzo negro. El oráculo leerá tus trazos y revelará lo oculto.")

# ============================
# API Key (Input inline, negro)
# ============================
with st.container():
    col_k1, col_k2 = st.columns([4,1])
    with col_k1:
        typed_key = st.text_input("Ingresa tu Clave Mágica (API Key) — usa Secrets si es posible",
                                  type="password", placeholder="sk-proj-…",
                                  key="typed_key",
                                  label_visibility="collapsed")
    with col_k2:
        st.markdown('<div class="small center" style="height:38px;">'
                    '🔒 Se prefiere usar <b>Secrets</b> en Deploy</div>', unsafe_allow_html=True)

api_key = get_api_key()
client = OpenAI(api_key=api_key) if api_key else None

# ============================
# Lienzo + Controles
# ============================
st.markdown("### Lienzo")
c1, c2 = st.columns([7,5])

with c1:
    st.markdown('<div class="block-card">', unsafe_allow_html=True)
    drawing_mode = "freedraw"
    # Defaults: fondo negro, trazo blanco
    canvas_result = st_canvas(
        fill_color="rgba(255,255,255,0.0)",
        stroke_width=6,
        stroke_color="#FFFFFF",
        background_color="#000000",
        height=420,
        width=720,
        drawing_mode=drawing_mode,
        key="canvas",
        update_streamlit=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="block-card">', unsafe_allow_html=True)
    st.markdown("#### Ajustes")
    stroke_width = st.slider("Grosor de la pluma", 1, 30, 6, key="stroke_w")
    stroke_color = st.color_picker("Color del trazo", "#FFFFFF", key="stroke_c")
    bg_color     = st.color_picker("Color del fondo", "#000000", key="bg_c")
    # Actualiza en vivo el canvas:
    if canvas_result is not None:
        pass
    st.markdown('<hr/>', unsafe_allow_html=True)
    ask_more = st.toggle("Añadir contexto místico", value=False)
    user_context = ""
    if ask_more:
        user_context = st.text_area("Escribe señales, símbolos o sensaciones:",
                                    placeholder="Es la primera imagen para nuestra etapa de prelanzamiento…",
                                    height=100)
    st.markdown('</div>', unsafe_allow_html=True)

# Botón centrado
st.write("")
center = st.columns([1,2,1])[1]
with center:
    analyze_button = st.button("Revelar mi futuro")

# ============================
# Acción
# ============================
if analyze_button:
    if not api_key:
        st.error("Por favor ingresa tu Clave Mágica o configúrala en Secrets (OPENAI_API_KEY).")
    elif canvas_result.image_data is None:
        st.warning("Dibuja algo en el lienzo antes de invocar al Oráculo.")
    else:
        with st.spinner("Consultando al Oráculo…"):
            # Guardar imagen a disco y codificar
            input_numpy = np.array(canvas_result.image_data)
            # Asegura 8-bit
            img = Image.fromarray(input_numpy.astype("uint8")).convert("RGBA")
            img.save("img.png")
            base64_image = encode_image_to_base64("img.png")
            st.session_state.base64_image = base64_image

            prompt_text = (
                "Eres un oráculo místico. Basado en este dibujo, interpreta el destino del usuario. "
                "Habla en tono enigmático y espiritual, como si revelaras un secreto profundo sobre su futuro. "
                "Usa metáforas, símbolos y un aire de misterio."
            )
            if user_context.strip():
                prompt_text += f"\n\nContexto adicional del consultante:\n{user_context.strip()}"

            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type":"text", "text": prompt_text},
                            {"type":"image_url",
                             "image_url":{"url": f"data:image/png;base64,{base64_image}"}}
                        ],
                    }],
                    max_tokens=500,
                )
                content = (resp.choices[0].message.content or "").strip()
                st.session_state.full_response = content
                st.session_state.analysis_done = True
            except Exception as e:
                st.error(f"Ocurrió un error en la lectura de tu destino: {e}")
                st.session_state.analysis_done = False

# ============================
# Resultado
# ============================
if st.session_state.analysis_done and st.session_state.full_response:
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("### 𓁻 Tu destino revelado 𓁻")
    st.markdown(f'<div class="block-card">{st.session_state.full_response}</div>', unsafe_allow_html=True)

    with st.spinner("Consultando un consejo del destino…"):
        try:
            consejo_prompt = (
                f"Basado en esta predicción del futuro: '{st.session_state.full_response}', "
                "genera un consejo espiritual y enigmático. "
                "Debe ser breve, inspirador y sonar como una guía del destino. "
                "Usa metáforas y un tono místico."
            )
            consejo = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":consejo_prompt}],
                max_tokens=180,
            ).choices[0].message.content
        except Exception as e:
            consejo = f"No se pudo obtener un consejo del destino: {e}"

    st.markdown("#### ⋆.˚ Consejo del destino ⋆.˚")
    st.markdown(f'<div class="block-card">{consejo}</div>', unsafe_allow_html=True)

# ============================
# Footer
# ============================
st.write("")
st.caption("Hecho para pantalla negra: tipografía blanca, acentos mínimos, foco en el contenido ✧")
