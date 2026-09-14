import streamlit as st
import google.generativeai as genai
import whisper
import os
# Importación moderna de MoviePy compatible con la nube actual
import moviepy as mp

st.set_page_config(page_title="Chimba AI Studio Pro", page_icon="🚀", layout="centered")

LINK_STRIPE_MENSUAL = "https://stripe.com"

if "es_pro" not in st.session_state:
    st.session_state.es_pro = False

with st.sidebar:
    st.header("👑 Tu Cuenta")
    if st.session_state.es_pro:
        st.success("Cuenta: PLAN PRO ACTIVO ✨")
    else:
        st.warning("Cuenta: PLAN GRATUITO 🛑")
        st.write("Desbloquea fuentes exclusivas y videos más largos.")
        st.markdown(f"[👉 Adquirir Plan PRO por $9.99/mes]({LINK_STRIPE_MENSUAL})")
        
        codigo_activacion = st.text_input("🔑 ¿Ya pagaste? Introduce tu código:")
        if codigo_activacion == "CHIMBAPRO2026": 
            st.session_state.es_pro = True
            st.success("¡Plan PRO activado con éxito!")
            st.rerun()

tab1, tab2 = st.tabs(["🧠 Cerebro (Guiones)", "🎬 Editor de Video"])

with tab1:
    st.title("🧠 Ideas, Guiones y Prompts")
    api_key = st.text_input("🔑 Pega tu API Key de Google AI Studio:", type="password")
    
    if api_key:
        api_key_clean = api_key.strip()
        try:
            genai.configure(api_key=api_key_clean)
            nicho = st.text_input("🔥 ¿De qué temática es tu canal?")
            estilo = st.selectbox("🎭 Tono:", ["Divertido y energético", "Serio y educativo", "Chismoso/Storytime"])
            
            if st.button("🚀 Generar Contenido"):
                if nicho:
                    with st.spinner("Pensando todo el contenido..."):
                        model = genai.GenerativeModel('gemini-3.6-flash')
                        prompt = f"Actúa como un experto en TikTok. Genera para el nicho '{nicho}' con tono '{estilo}': 1. Idea viral. 2. Guión de 45s. 3. 3 prompts detallados en inglés para generar imágenes de fondo en IAs gratis."
                        response = model.generate_content(prompt)
                        st.success("¡Estrategia lista!")
                        st.markdown(response.text)
        except Exception as e:
            st.error(f"🚨 Problema: {e}")

with tab2:
    st.title("🎬 Editor Inteligente")
    
    video_file = st.file_uploader("📂 Sube tu video (.mp4)", type=["mp4", "mov"])
    
    if video_file:
        with open("video_input.mp4", "wb") as f:
            f.write(video_file.read())
            
        st.video("video_input.mp4")
        
        st.subheader("🎨 Configurar Subtítulos")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            color_sub = st.selectbox("🎨 Color:", ["YELLOW", "WHITE", "GREEN", "CYAN"])
            
        with col2:
            if st.session_state.es_pro:
                fuente_sub = st.selectbox("🔤 Fuente (Letra):", ["Liberation-Sans-Bold", "DejaVu-Sans-Bold", "Courier-Bold"])
            else:
                fuente_sub = st.selectbox("🔤 Fuente (Letra):", ["Liberation-Sans-Bold"], help="¡Plan PRO para desbloquear más fuentes!")
                
        with col3:
            tamano_sub = st.slider("📏 Tamaño:", 24, 60, 36)
        
        if st.button("⚡ Procesar Video"):
            with st.spinner("Editando video..."):
                try:
                    video_final_path = "video_input.mp4"
                    
                    model_whisper = whisper.load_model("base")
                    result = model_whisper.transcribe(video_final_path, language="es")
                    
                    # Llamadas con la nueva estructura de MoviePy
                    video = mp.VideoFileClip(video_final_path)
                    clips_texto = []
                    
                    for segment in result["segments"]:
                        texto = segment["text"].upper()
                        inicio = segment["start"]
                        fin = segment["end"]
                        
                        txt_clip = mp.TextClip(texto, fontsize=tamano_sub, color=color_sub.lower(), font=fuente_sub, method='caption', size=(video.w*0.8, None))
                        txt_clip = txt_clip.set_start(inicio).set_end(fin).set_position(('center', 'center'))
                        clips_texto.append(txt_clip)
                    
                    video_editado = mp.CompositeVideoClip([video] + clips_texto)
                        
                    if not st.session_state.es_pro:
                        st.info("Añadiendo marca de agua protectora (Plan Gratis)")
                        marca = mp.TextClip("Hecho con Chimba AI", fontsize=20, color='white', font='Liberation-Sans-Bold')
                        marca = marca.set_start(0).set_end(video.duration).set_position(('right', 'top'))
                        video_editado = mp.CompositeVideoClip([video_editado, marca])
                        
                    video_editado.write_videofile("video_renderizado.mp4", fps=video.fps, codec="libx264", audio_codec="aac", verbose=False, logger=None)
                    
                    st.success("🔥 ¡Tu video está listo!")
                    st.video("video_renderizado.mp4")
                    
                except Exception as e:
                    st.error(f"🚨 Error: {e}")
