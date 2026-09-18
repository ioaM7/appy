import streamlit as st
from pypdf import PdfReader
from gtts import gTTS
from groq import Groq

# Configuración de la página para celulares
st.set_page_config(
    page_title="AudioApunte Express",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ AudioApunte Universitario")
st.caption("Resume y escucha tus lecturas para momentos de apuro")

# 1. Intentar obtener la API Key desde Secrets de Streamlit o desde la barra lateral
groq_api_key = ""
if "GROQ_API_KEY" in st.secrets:
    groq_api_key = st.secrets["GROQ_API_KEY"]

with st.sidebar:
    st.header("⚙️ Configuración")
    input_key = st.text_input("Ingresa tu Groq API Key (gsk_...):", value=groq_api_key, type="password")
    if input_key:
        groq_api_key = input_key

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
            extracted = "".join([page.extract_text() or "" for page in reader.pages])
            raw_text = extracted
            st.success(f"PDF cargado con éxito ({len(reader.pages)} páginas).")
        except Exception as e:
            st.error(f"Error al leer el PDF: {e}")

# Botón de Procesamiento
if st.button("🚀 Generar Explicación y Audio", type="primary"):
    if not groq_api_key:
        st.warning("Por favor ingresa tu API Key de Groq en la barra lateral o guárdala en Secrets.")
    elif not raw_text.strip():
        st.warning("Por favor ingresa texto o sube un PDF antes de continuar.")
    else:
        with st.spinner("Procesando lectura con Llama-3 en Groq y generando audio..."):
            try:
                # Inicializar el cliente de Groq
                client = Groq(api_key=groq_api_key)

                prompt = f"""
                Actúa como un profesor universitario cercano, claro y didáctico. 
                Explica el siguiente texto académico en un RELATO CONTINUO Y EN PÁRRAFOS NARRATIVOS (estilo podcast fluido), listo para ser leído en voz alta.
                
                REGLAS:
                - NO uses listas, viñetas, subtítulos ni secciones.
                - Resume la tesis principal, los autores y los conceptos clave en 3 a 4 párrafos claros.
                - Usa analogías sencillas pero mantén la terminología técnica adecuada.
                - Responde OBLIGATORIAMENTE en idioma ESPAÑOL.

                Texto a resumir:
                {raw_text[:12000]}
                """

                # Petición a la API de Groq usando Llama 3
                completion = client.chat.completions.create(
                    model="llama-3.3-70B-versatile",
                    messages=[
                        {"role": "system", "content": "Eres un asistente académico experto que resume textos universitarios en español claro y fluido."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=1024
                )

                summary = completion.choices[0].message.content

                # Mostrar la transcripción
                st.subheader("📝 Transcripción del Resumen:")
                st.write(summary)

                # Generar el audio MP3 con Google TTS
                tts = gTTS(text=summary, lang='es', slow=False)
                audio_file = "resumen.mp3"
                tts.save(audio_file)

                # Mostrar reproductor de audio
                st.subheader("🎧 Escuchar Resumen:")
                st.audio(audio_file, format="audio/mp3")

            except Exception as e:
                st.error(f"Ocurrió un error al procesar el audio: {e}")
