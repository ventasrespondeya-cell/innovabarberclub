import streamlit as st
import datetime
from google_calendar import GoogleCalendarManager
from google_sheets import GoogleSheetsManager
from email_sender import EmailSender

# ==========================================
# CONFIGURACIÓN DE TUS DATOS (MANTÉN TUS IDs AQUÍ)
# ==========================================
CALENDAR_ID = "dd8ede64704314d1f73f0f3c8be1c94a01f5710a641e3bf37a858fb37d9f4e44@group.calendar.google.com"
SPREADSHEET_ID = "1jZfdVpdG9WdUpz0gN_dqPLxKFIMjJBHypd2NvbnR-rM"
REMITENTE_EMAIL = "tu_correo@gmail.com"
PASSWORD_EMAIL = "tu_contraseña_de_aplicacion"

# Instancias de los gestores
calendar_manager = GoogleCalendarManager()
sheets_manager = GoogleSheetsManager()
email_sender = EmailSender(REMITENTE_EMAIL, PASSWORD_EMAIL)

# ==========================================
# CONFIGURACIÓN VISUAL VIP (INNOVA BARBER CLUB)
# ==========================================
st.set_page_config(
    page_title="Innova Barber Club | Reservas",
    page_icon="💈",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Inyección de CSS para un estilo oscuro, premium y elegante
st.markdown("""
    <style>
    /* Fondo principal y textos */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Títulos con estilo premium */
    h1, h2, h3 {
        color: #D4AF37 !important; /* Dorado elegante */
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Estilo del contenedor del formulario */
    div[data-testid="stForm"] {
        background-color: #1A1C23;
        border: 1px solid #D4AF37;
        border-radius: 10px;
        padding: 30px;
        box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.1);
    }
    
    /* Botón de confirmación (Dorado) */
    .stButton>button {
        background-color: #D4AF37;
        color: #000000;
        border-radius: 5px;
        height: 3.5em;
        width: 100%;
        font-weight: 800;
        font-size: 16px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FFDF70;
        color: #000000;
        transform: scale(1.02);
    }
    
    /* Inputs y selectores */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea, .stDateInput input {
        background-color: #262730;
        color: white;
        border-radius: 5px;
        border: 1px solid #4B4B4B;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# BARRA LATERAL (INFORMACIÓN DEL NEGOCIO)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>INNOVA<br><span style='color: #D4AF37;'>BARBER CLUB</span></h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.write("📍 **Ubicación:**")
    st.write("*(Reemplaza aquí con la dirección exacta de su perfil de IG)*")
    st.write("🕒 **Horario de Atención:**")
    st.write("Lunes a Sábado: 09:00 AM - 07:00 PM")
    st.write("📱 **Contacto / WhatsApp:**")
    st.write("+58 (Inserta su número aquí)")
    st.markdown("---")
    st.info("💡 Llega 5 minutos antes para disfrutar de un café o bebida de cortesía antes de tu servicio.")

# ==========================================
# PANTALLA PRINCIPAL
# ==========================================
st.markdown("<h1 style='text-align: center;'>💈 AGENDA TU CITA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A0A0A0; font-size: 18px;'>Bienvenido a Innova Barber Club. Selecciona tu servicio y asegura tu espacio con nuestros barberos profesionales.</p>", unsafe_allow_html=True)
st.write("")

# ==========================================
# FORMULARIO DE RESERVA
# ==========================================
with st.form("form_reserva"):
    st.markdown("<h3 style='margin-bottom: 20px;'>Tus Datos</h3>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        nombre = st.text_input("Nombre y Apellido *")
    with col_b:
        email = st.text_input("Correo Electrónico *")
        
    st.markdown("<h3 style='margin-top: 20px; margin-bottom: 20px;'>El Servicio</h3>", unsafe_allow_html=True)
    servicio = st.selectbox("Selecciona tu estilo *", [
        "Corte Clásico / Tradicional ($10)", 
        "Fade / Degradado Premium ($12)",
        "Perfilado y Diseño de Barba ($8)", 
        "Corte + Barba (Servicio Completo) ($18)",
        "Limpieza Facial VIP ($15)",
        "Corte + Barba + Facial (Experiencia Innova) ($30)"
    ])
    
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Día de la cita *", min_value=datetime.date.today())
    
    # Lógica de filtrado de horas ocupadas
    todas_las_horas = [datetime.time(h, m) for h in range(9, 19) for m in (0, 30)]
    
    try:
        horas_ocupadas_str = calendar_manager.obtener_eventos_del_dia(CALENDAR_ID, fecha)
    except Exception:
        horas_ocupadas_str = []

    horas_disponibles = [
        h for h in todas_las_horas 
        if h.strftime("%H:%M") not in horas_ocupadas_str
    ]

    with col2:
        if horas_disponibles:
            hora = st.selectbox(
                "Hora disponible *", 
                horas_disponibles, 
                format_func=lambda x: x.strftime("%I:%M %p")
            )
        else:
            st.warning("⚠️ No hay horarios disponibles para este día.")
            hora = None
        
    notas = st.text_area("¿Alguna preferencia de barbero o detalle especial? (Opcional)")
    
    st.write("")
    submit_button = st.form_submit_button("RESERVAR MI ESPACIO")

# ==========================================
# LÓGICA DE PROCESAMIENTO
# ==========================================
if submit_button:
    if not hora:
        st.error("⚠️ No hay un horario disponible o seleccionado para este día.")
    elif not nombre or not email:
        st.error("⚠️ Por favor, completa tu Nombre y Correo Electrónico.")
    else:
        with st.spinner("Confirmando tu reserva en nuestro sistema..."):
            try:
                # 1. Crear evento en Google Calendar
                fecha_hora_combinada = datetime.datetime.combine(fecha, hora)
                nombre_servicio_corto = servicio.split(' (')[0]
                resumen_evento = f"Innova: {nombre_servicio_corto} - {nombre}"
                descripcion_evento = f"Cliente: {nombre}\nEmail: {email}\nNotas: {notas}"
                
                calendar_manager.crear_evento(
                    calendar_id=CALENDAR_ID,
                    resumen=resumen_evento,
                    descripcion=descripcion_evento,
                    fecha_inicio=fecha_hora_combinada
                )
                
                # 2. Registrar en Google Sheets
                datos_sheet = [
                    str(fecha),
                    hora.strftime("%I:%M %p"),
                    nombre,
                    email,
                    servicio,
                    notas
                ]
                sheets_manager.agregar_reserva(SPREADSHEET_ID, datos_sheet)
                
                # 3. Enviar correo de confirmación
                email_sender.enviar_confirmacion(
                    destinatario=email,
                    nombre_cliente=nombre,
                    servicio=nombre_servicio_corto,
                    fecha=str(fecha),
                    hora=hora.strftime("%I:%M %p")
                )
                
                st.success(f"✔️ ¡Reserva confirmada! Te esperamos el {fecha} a las {hora.strftime('%I:%M %p')}.")
                st.balloons()
                
            except Exception as e:
                st.error(f"Ocurrió un error de conexión: {e}")