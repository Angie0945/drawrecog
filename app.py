import os
import streamlit as st
import base64
import numpy as np
from openai import OpenAI
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title='Tablero Inteligente', layout='wide')

# Estilos personalizados para contraste y centrado
st.markdown("""
    <style>
    .stCanvas {
        margin: 0 auto;
        border: 2px solid #6f42c1 !important;
        border-radius: 10px;
    }
    .main-title {
        text-align: center;
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE UTILIDAD ---
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("🎨 Configuración")
    st.info("Esta IA interpreta tus bocetos usando GPT-4o.")
    
    stroke_width = st.slider('Grosor del trazo', 1, 30, 5)
    
    st.markdown("---")
    st.subheader("🔑 Seguridad")
    api_key = st.text_input("OpenAI API Key", type="password", help="Tu clave no se guardará permanentemente.")
    
    st.markdown("---")
    st.caption("Desarrollado para análisis de visión artificial.")

# --- CUERPO PRINCIPAL ---
st.markdown("<h1 class='main-title'>🖋️ Tablero Inteligente</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Dibuja un concepto y deja que la IA lo describa</h4>", unsafe_allow_html=True)

# Columnas para centrar el lienzo
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Configuración solicitada: Fondo Lila, Letra Negra
    bg_color = "#E0BBE4"  # Lila claro
    stroke_color = "#000000" # Negro para alto contraste
    
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=350,
        width=450,
        drawing_mode="freedraw",
        key="canvas",
    )

    analyze_button = st.button("🚀 Analizar boceto", use_container_width=True)

# --- LÓGICA DE PROCESAMIENTO ---
if analyze_button:
    if not api_key:
        st.error("⚠️ Por favor, ingresa tu API Key en la barra lateral.")
    elif canvas_result.image_data is not None:
        try:
            client = OpenAI(api_key=api_key)
            
            with st.spinner("La IA está observando tu dibujo..."):
                # 1. Guardar imagen temporalmente
                input_numpy_array = np.array(canvas_result.image_data)
                input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
                input_image.save('temp_boceto.png')
                
                # 2. Codificar
                base64_image = encode_image_to_base64('temp_boceto.png')
                
                # 3. Llamada a OpenAI
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Describe en español de forma breve y creativa qué ves en este boceto."},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                                },
                            ],
                        }
                    ],
                    max_tokens=300,
                )
                
                # 4. Mostrar resultado
                resultado = response.choices[0].message.content
                st.markdown("---")
                st.subheader("📝 Análisis de la IA:")
                st.success(resultado)
                
        except Exception as e:
            st.error(f"Hubo un error con la API: {e}")
    else:
        st.warning("El lienzo está vacío. ¡Dibuja algo primero!")
