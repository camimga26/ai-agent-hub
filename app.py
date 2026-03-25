import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# ─── CONFIGURACIÓN INICIAL ─────────────────────────────────────────────────────
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Modelo gratuito de OpenRouter — no requiere créditos
MODEL = "openrouter/free"

# ─── DEFINICIÓN DE LOS 4 AGENTES ──────────────────────────────────────────────
AGENTS = {
    "💬 Chat General": {
        "system": (
            "Eres un asistente de IA útil, amigable y directo. "
            "Respondes en el idioma del usuario. Eres conciso pero completo. "
            "Tienes memoria de toda la conversación y la usas para dar respuestas coherentes."
        ),
        "description": "Tu asistente general. Habla de cualquier tema con memoria completa.",
        "placeholder": "¿En qué te puedo ayudar hoy?",
    },
    "✍️ Creador de Contenido": {
        "system": (
            "Eres un experto creador de contenido digital con 10 años de experiencia. "
            "Creas posts virales con ganchos poderosos para Instagram, TikTok, Twitter y LinkedIn. "
            "Usas emojis estratégicamente. Si el usuario no especifica la plataforma, la preguntas. "
            "Siempre das 2 o 3 variantes del contenido para que el usuario elija la mejor. "
            "Adaptas el tono: energético para TikTok, visual para Instagram, conciso para Twitter."
        ),
        "description": "Crea posts virales para Instagram, TikTok, Twitter y LinkedIn.",
        "placeholder": "Ej: Crea un post de TikTok sobre emprendimiento para jóvenes",
    },
    "💻 Asistente de Código": {
        "system": (
            "Eres un programador senior experto en Python, JavaScript, Java, HTML, CSS y más. "
            "Cuando el usuario comparte código con un error: "
            "1) Identificas el problema exacto en una línea. "
            "2) Explicas en términos simples por qué ocurre. "
            "3) Muestras el código corregido completo con comentarios. "
            "Siempre usas bloques de código con el lenguaje especificado. "
            "Si el usuario pide que escribas código, lo haces limpio, con comentarios y listo para usar."
        ),
        "description": "Explica errores, depura y escribe código en cualquier lenguaje.",
        "placeholder": "Pega tu código aquí o describe qué quieres construir...",
    },
    "📚 Tutor de Estudio": {
        "system": (
            "Eres un tutor experto, paciente y muy claro. Puedes hacer cuatro cosas: "
            "1) RESUMIR: Condensas textos largos en los puntos clave más importantes. "
            "2) EXPLICAR: Tomas conceptos difíciles y los explicas con analogías simples. "
            "3) QUIZ: Creas preguntas de repaso con respuestas para autoevaluación. "
            "4) ESQUEMA: Organizas un tema en un esquema visual con jerarquía clara. "
            "Siempre preguntas qué quiere el estudiante si no está claro."
        ),
        "description": "Resume textos, explica conceptos y genera preguntas de repaso.",
        "placeholder": "Pega el texto a resumir o escribe el tema que quieres entender...",
    },
}

# ─── CONFIGURACIÓN DE LA PÁGINA ────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Agent Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── ESTILOS CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        .stApp { background-color: #0f0f1a; color: #E5E7EB; }
        [data-testid="stSidebar"] {
            background-color: #13131f !important;
            border-right: 1px solid #2D2D44;
        }
        .main-title {
            font-size: 2.2rem; font-weight: 800;
            background: linear-gradient(90deg, #6366F1, #EC4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .agent-subtitle { color: #9CA3AF; font-size: 0.95rem; margin-top: 4px; }
        [data-testid="stChatMessage"] {
            background-color: #1a1a2e;
            border-radius: 12px;
            border: 1px solid #2D2D44;
            margin-bottom: 8px;
        }
        hr { border-color: #2D2D44; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── MEMORIA: SESSION STATE ────────────────────────────────────────────────────
# histories guarda lista de dicts {"role": "user"/"assistant", "content": "..."}
# Este formato es el estándar de OpenAI que OpenRouter también usa
if "histories" not in st.session_state:
    st.session_state.histories = {name: [] for name in AGENTS}

if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = "💬 Chat General"

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 AI Agent Hub")
    st.markdown("<small style='color:#6B7280'>Selecciona un agente</small>", unsafe_allow_html=True)
    st.markdown("---")

    for agent_name in AGENTS:
        is_active = st.session_state.selected_agent == agent_name
        if st.button(
            agent_name,
            key=f"btn_{agent_name}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.selected_agent = agent_name
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Limpiar esta conversación", use_container_width=True):
        st.session_state.histories[st.session_state.selected_agent] = []
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<small style='color:#6B7280'>Powered by OpenRouter<br>Built by Cami 🚀</small>",
        unsafe_allow_html=True,
    )

# ─── ÁREA PRINCIPAL ───────────────────────────────────────────────────────────
current_agent_name = st.session_state.selected_agent
current_agent = AGENTS[current_agent_name]

st.markdown('<h1 class="main-title">AI Agent Hub</h1>', unsafe_allow_html=True)
st.markdown(
    f'<p class="agent-subtitle"><strong>{current_agent_name}</strong> — {current_agent["description"]}</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ─── MOSTRAR HISTORIAL ────────────────────────────────────────────────────────
for message in st.session_state.histories[current_agent_name]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─── INPUT Y RESPUESTA ────────────────────────────────────────────────────────
user_input = st.chat_input(current_agent["placeholder"])

if user_input:
    # 1. Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Agregar al historial
    st.session_state.histories[current_agent_name].append({
        "role": "user",
        "content": user_input,
    })

    # 3. Construir mensajes: system prompt + historial completo (esto es la memoria)
    messages_to_send = [
        {"role": "system", "content": current_agent["system"]}
    ] + st.session_state.histories[current_agent_name]

    # 4. Llamar a OpenRouter y mostrar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages_to_send,
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

    # 5. Guardar respuesta del agente en el historial
    st.session_state.histories[current_agent_name].append({
        "role": "assistant",
        "content": reply,
    })
