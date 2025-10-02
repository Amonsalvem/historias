import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

Variables

Expert = " "
profile_imgenh = " "

Inicializar session_state

if 'analysis_done' not in st.session_state:
st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
st.session_state.base64_image = ""

def encode_image_to_base64(image_path):
try:
with open(image_path, "rb") as image_file:
encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
return encoded_image
except FileNotFoundError:
return "Error: La imagen no se encontró en la ruta especificada."

🌌 Interfaz principal

st.set_page_config(page_title='🔮 Tablero Místico', layout="wide")
st.title('🔮 Tablero Místico de Predicciones')

st.markdown("""
✨ Bienvenido/a al Oráculo Digital ✨
Lo que traces aquí no será un simple dibujo...
Cada línea, cada trazo y cada forma revelará lo oculto en tu mente, y con ello... tu destino.

Dibuja sin pensar, deja que tu intuición guíe tu mano.
Cuando estés listo, pide al tablero que revele lo que el futuro guarda para ti.
""")

🎨 Panel lateral

with st.sidebar:
st.subheader("⚙️ Herramientas de tu destino")
stroke_width = st.slider('📏 Grosor de la pluma', 1, 30, 5)
stroke_color = st.color_picker("🎨 Color de tu energía", "#000000")
bg_color = st.color_picker("🌌 Color del universo", "#FFFFFF")

🎨 Canvas para dibujar

drawing_mode = "freedraw"
canvas_result = st_canvas(
fill_color="rgba(255, 165, 0, 0.3)",
stroke_width=stroke_width,
stroke_color=stroke_color,
background_color=bg_color,
height=350,
width=450,
drawing_mode=drawing_mode,
key="canvas",
)

🔑 API Key

ke = st.text_input('🔑 Ingresa tu Clave Mágica (API Key)', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

🔮 Botón para análisis

analyze_button = st.button("🔮 Revela mi futuro", type="primary")

if canvas_result.image_data is not None and api_key and analyze_button:

with st.spinner("✨ Consultando a los espíritus del código..."):
    input_numpy_array = np.array(canvas_result.image_data)
    input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
    input_image.save('img.png')

    base64_image = encode_image_to_base64("img.png")
    st.session_state.base64_image = base64_image

    prompt_text = (
        f"Eres un oráculo místico. Basado en este dibujo, interpreta el destino del usuario. "
        f"Habla en tono enigmático y espiritual, como si estuvieras revelando un secreto profundo sobre su futuro. "
        f"Predice con metáforas, símbolos y un aire de misterio."
    )

    try:
        full_response = ""
        message_placeholder = st.empty()
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                        },
                    ],
                }
            ],
            max_tokens=500,
        )

        if response.choices[0].message.content is not None:
            full_response += response.choices[0].message.content
            message_placeholder.markdown(full_response)

        st.session_state.full_response = full_response
        st.session_state.analysis_done = True

    except Exception as e:
        st.error(f"Ocurrió un error en la lectura de tu destino: {e}")

Mostrar resultado

if st.session_state.analysis_done:
st.divider()
st.subheader("🌙 Tu destino revelado:")
st.markdown(f"✨ {st.session_state.full_response} ✨")

if not api_key:
st.warning("⚠️ Ingresa tu Clave Mágica para invocar al Oráculo.")
