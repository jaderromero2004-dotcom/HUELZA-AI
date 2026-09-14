import streamlit as st
import google.generativeai as genai
import whisper
import os
import moviepy as mp

st.set_page_config(page_title="Huelza AI Studio", page_icon="🚀", layout="centered")

# 🔐 INTENTO DE LEER LA API KEY ESCONDIDA EN EL SERVIDOR
# Si no está configurada en los Secrets de Streamlit, usará una casilla de emergencia
api_key_servidor = st.secrets.get("GOOGLE_API_KEY", "")

LINK_STRIPE_MENSUAL = "https://stripe.com"

if "es_pro" not in st.session_state:
    st.session_state.es_pro = False

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("👑 Tu Cuenta")
    if st.session_state.es_pro:
        st.success("Cuenta: PLAN PRO ACTIVO ✨")
    else:
        st.warning("Cuenta: PLAN GRATUITO 🛑")
        st.write("Desbloquea ganchos premium, estilos de famosos y subtítulos avanzados.")
        st.markdown(f"[👉 Adquirir Plan PRO por $9.99/mes]({LINK_STRIPE_MENSUAL})")
        
        codigo_activacion = st.text_input("🔑 ¿Ya pagaste? Introduce tu código:")
        if codigo_activacion == "CHIMBAPRO2026": 
            st.session_state.es_pro = True
            st.success("¡Plan PRO activado con éxito!")
            st.rerun()

# --- VALIDACIÓN DE LA API KEY TRAS BAMBALINAS ---
if api_key_servidor:
    genai.configure(api_key=api_key_servidor)
    ia_activa = True
else:
    # Casilla de emergencia por si no has configurado los Secrets todavía
    api_key_manual = st.text_input("🔑 [Modo Administrador] Pega tu API Key para activar la app:", type="password")
    if api_key_manual:
        genai.configure(api_key=api_key_manual.strip())
        ia_activa = True
    else:
        ia_activa = False

tab1, tab2 = st.tabs(["🧠 Cerebro (Guiones)", "🎬 Editor de Video"])

with tab1:
    st.title("🧠 Ideas, Guiones y Prompts")
    st.write("Genera contenido diseñado para viralizar en segundos.")
    
    if not ia_activa:
        st.info("Configurando los motores de IA del servidor... Por favor espera.")
    else:
        nicho = st.text_input("🔥 ¿De qué temática es tu canal? (Ej: Finanzas para jóvenes, Gym)")
        
        # FUNCIONES PRO DESBLOQUEADAS
        if st.session_state.es_pro:
            estilo_famoso = st.selectbox("🎭 Clonar estilo de narración (PRO):", ["Estilo dinámico (MrBeast)", "Estilo Vendedor/Agresivo", "Estilo Educativo/Storytime (TED)", "Estilo Conspirativo/Misterio"])
            formato_salida = st.multiselect("📦 Formatos a generar (PRO):", ["Guión de TikTok (Vertical)", "Hilo de X / Twitter", "Texto para Carrusel de Instagram"], default=["Guión de TikTok (Vertical)"])
        else:
            estilo_famoso = "Estilo Estándar"
            st.caption("🔒 *Desbloquea el PLAN PRO para clonar estilos de creadores famosos y generar múltiples formatos a la vez.*")
        
        estilo_tono = st.selectbox("🎭 Tono de la voz:", ["Divertido y energético", "Serio y educativo", "Sarcástico y rápido"])
        
        if st.button("🚀 Generar Contenido"):
            if nicho:
                with st.spinner("La IA está cocinando tu estrategia..."):
                    try:
                        model = genai.GenerativeModel('gemini-3.6-flash')
                        
                        # Armamos un prompt mucho más potente si el usuario es PRO
                        if st.session_state.es_pro:
                            prompt = f"""
                            Actúa como un director creativo experto en viralización. Genera para el nicho '{nicho}' con tono '{estilo_tono}' imitando un '{estilo_famoso}'.
                            Formatos requeridos: {formato_salida}.
                            Entrega:
                            1. 💡 IDEA VIRAL REVOLUCIONARIA.
                            2. 🎬 GUIÓN PRINCIPAL (Con ganchos psicológicos alternativos para pruebas A/B).
                            3. 💬 COMENTARIO FIJADO ESTRATÉGICO (Diseñado para forzar debates y comentarios).
                            4. 🖼️ 3 PROMPTS EN INGLÉS para generar imágenes de fondo espectaculares.
                            """
                        else:
                            prompt = f"Genera una idea básica y un guión estándar de 45 segundos para el nicho '{nicho}' con tono '{estilo_tono}'. Incluye 3 hashtags."
                        
                        response = model.generate_content(prompt)
                        st.success("¡Estrategia lista!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"🚨 Error en los motores: {e}")

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
                fuente_sub = st.selectbox("🔤 Fuente (Letra) PRO:", ["Liberation-Sans-Bold", "DejaVu-Sans-Bold", "Courier-Bold"])
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
                        marca = mp.TextClip("Hecho con Huelza AI", fontsize=20, color='white', font='Liberation-Sans-Bold')
                        marca = marca.set_start(0).set_end(video.duration).set_position(('right', 'top'))
                        video_editado = mp.CompositeVideoClip([video_editado, marca])
                        
                    video_editado.write_videofile("video_renderizado.mp4", fps=video.fps, codec="libx264", audio_codec="aac", verbose=False, logger=None)
                    st.success("🔥 ¡Tu video está listo!")
                    st.video("video_renderizado.mp4")
                except Exception as e:
                    st.error(f"🚨 Error: {e}")
