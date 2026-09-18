import streamlit as st
from pypdf import PdfReader
from gtts import gTTS
import os
import google.genai as genai

# Configuración de la página para celulares
st.set_page_config(
    page_title="AudioApunte Express",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ AudioApunte Universitario")
st.caption("Resume y escucha tus lecturas para momentos de apuro")

# Entrada para el API Key o Token en la barra lateral
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("Ingresa tu Gemini API Key / Auth Token:", type="password")
    st.info("Obtén tu clave en Google AI Studio.")

# Selector de origen de texto
option = st.radio("¿Qué deseas procesar?", ("Texto Copiado", "Subir PDF"))

raw_text = ""

if option == "Texto Copiado":
    raw_text = st.text_area("Pega aquí el texto de la materia:", height=200)

elif option == "Subir PDF":
    uploaded_file = st.file_uploader("Elige un archivo PDF", type=["pdf"])
    if uploaded_file is not None:
        try:
            reader = PdfReader(uploaded_file)
            extracted = ""
            for page in reader.pages:
                extracted += page.extract_text() or ""
            raw_text = extracted
            st.success(f"PDF cargado con éxito ({len(reader.pages)} páginas).")
        except Exception as e:
            st.error(f"Error al leer el PDF: {e}")

# Botón de Procesamiento
if st.button("🚀 Generar Explicación y Audio", type="primary"):
    if not api_key:
        st.warning("Por favor ingresa tu clave/token en la barra lateral izquierda.")
    elif not raw_text.strip():
        st.warning("Por favor ingresa texto o sube un PDF antes de continuar.")
    else:
        with st.spinner("Procesando lectura con IA y generando audio..."):
            try:
                # Inicializar el cliente de Gemini
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
                Actúa como un profesor universitario cercano, claro y didáctico. 
                Explica el siguiente texto académico en un RELATO CONTINUO Y EN PÁRRAFOS NARRATIVOS (estilo podcast fluido), listo para ser leído en voz alta.
                
                REGLAS:
                - NO uses listas, viñetas, subtítulos ni secciones.
                - Resume la tesis principal, los autores y los conceptos clave en 3 a 4 párrafos claros.
                - Usa analogías sencillas pero mantén la terminología técnica adecuada.

                Texto:
                {raw_text[:12000]}
                """

                # Llamada usando el modelo estable gemini-1.5-flash
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt
                )
                
                summary = response.text

                # Mostrar el texto generado
                st.subheader("📝 Transcripción del Resumen:")
                st.write(summary)

                # Generar el audio MP3 con Google TTS
                tts = gTTS(text=summary, lang='es', slow=False)
                audio_file = "resumen.mp3"
                tts.save(audio_file)

                # Mostrar el reproductor de audio integrado
                st.subheader("🎧 Escuchar Resumen:")
                st.audio(audio_file, format="audio/mp3")

            except Exception as e:
                st.error(f"Ocurrió un error al procesar el audio: {e}")
