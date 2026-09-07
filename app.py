import streamlit as st
import datetime
import re
from google_calendar import GoogleCalendarManager
from google_sheets import GoogleSheetsManager
from email_sender import EmailSender

# ==========================================
# CONFIGURACIÓN DE TUS DATOS DE BACKEND
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
# CONFIGURACIÓN VISUAL VIP
# ==========================================
st.set_page_config(
    page_title="Innova Barber Club | Citas VIP",
    page_icon="💈",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Inyección de CSS Avanzado
st.markdown("""
    <style>
    /* Fondo principal y textos */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Tipografía y encabezados */
    h1, h2, h3 {
        color: #D4AF37 !important;
        font-family: 'Helvetica Neue', sans-serif;
        letter-spacing: 0.5px;
    }
    
    /* Contenedor del formulario */
    div[data-testid="stForm"] {
        background-color: #16181E;
        border: 1px solid #D4AF37;
        border-radius: 12px;
        padding: 28px;
        box-shadow: 0px 6px 20px rgba(212, 175, 55, 0.12);
    }
    
    /* Botón Dorado Principal */
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #AA820A 100%);
        color: #000000;
        border-radius: 6px;
        height: 3.6em;
        width: 100%;
        font-weight: 800;
        font-size: 16px;
        border: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #FFDF70 0%, #D4AF37 100%);
        color: #000000;
        transform: translateY(-2px);
    }
    
    /* Modificación de Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea, .stDateInput input {
        background-color: #21232B;
        color: #FFFFFF;
        border-radius: 6px;
        border: 1px solid #3A3D4A;
    }
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus {
        border-color: #D4AF37;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# BARRA LATERAL (DATOS OFICIALES)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>INNOVA<br><span style='color: #D4AF37;'>BARBER CLUB</span></h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("📍 **Ubicación:**")
    st.write("Av. Francia, C.C. Divina Pastora")
    st.caption("Barinas, Venezuela")
    
    st.markdown("🕒 **Horarios de Atención:**")
    st.write("Lunes a Sábado: 09:00 AM - 07:00 PM")
    
    st.markdown("📱 **Contacto Directo:**")
    st.write("0412-0266809")
    
    st.markdown("---")
    st.info("💡 **Cortesía Innova:** Incluye servicio de café, bebida refrescante y Wi-Fi en cada sesión.")

# ==========================================
# PANTALLA PRINCIPAL
# ==========================================
st.markdown("<h1 style='text-align: center;'>💈 RESERVA TU CITA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A0A0A0; font-size: 16px;'>Asegura tu turno con nuestros especialistas de estilo. Selección rápida y confirmación al instante.</p>", unsafe_allow_html=True)
st.write("")

# Formulario de Reserva con Lógica de Validación
with st.form("form_reserva"):
    st.markdown("<h3 style='margin-bottom: 15px;'>1. Información de Contacto</h3>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        nombre = st.text_input("Nombre y Apellido *", placeholder="Ej. Carlos Pérez")
        telefono = st.text_input("Número de Teléfono *", placeholder="Ej. 0412-0266809")
    with col_b:
        email = st.text_input("Correo Electrónico *", placeholder="ejemplo@correo.com")
        
    st.markdown("<h3 style='margin-top: 20px; margin-bottom: 15px;'>2. Detalle del Servicio</h3>", unsafe_allow_html=True)
    servicio = st.selectbox("Selecciona la experiencia *", [
        "Corte Clásico / Tradicional ($10)", 
        "Fade / Degradado Premium ($12)",
        "Perfilado y Diseño de Barba ($8)", 
        "Corte + Barba (Servicio Completo) ($18)",
        "Limpieza Facial VIP ($15)",
        "Corte + Barba + Facial (Experiencia Innova) ($30)"
    ])
    
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Día preferido *", min_value=datetime.date.today())
    
    # Lógica avanzada para filtrado de citas
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
                "Horario disponible *", 
                horas_disponibles, 
                format_func=lambda x: x.strftime("%I:%M %p")
            )
        else:
            st.warning("⚠️ Sin turnos disponibles para este día.")
            hora = None
        
    notas = st.text_area("Notas o preferencias sobre tu corte/barbero (Opcional)")
    
    st.write("")
    submit_button = st.form_submit_button("CONFIRMAR Y AGENDAR CITA")

# ==========================================
# LÓGICA DE PROCESAMIENTO Y VALIDACIÓN
# ==========================================
if submit_button:
    # Expresiones regulares para validaciones
    patron_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    patron_telefono = r"^(0412|0414|0424|0416|0426)[0-9]{7}$"
    telefono_limpio = re.sub(r"[\s\-\(\)]", "", telefono)

    if not hora:
        st.error("⚠️ No hay un horario disponible seleccionado para este día.")
    elif not nombre.strip():
        st.error("⚠️ Por favor, ingresa tu Nombre y Apellido.")
    elif not re.match(patron_email, email):
        st.error("⚠️ Por favor, ingresa un Correo Electrónico válido (ejemplo@dominio.com).")
    elif not re.match(patron_telefono, telefono_limpio):
        st.error("⚠️ Ingresa un número de teléfono válido (Ej: 04120266809 o 0412-0266809).")
    else:
        with st.spinner("Procesando tu cita en tiempo real..."):
            try:
                # 1. Crear evento en Google Calendar
                fecha_hora_combinada = datetime.datetime.combine(fecha, hora)
                nombre_servicio_corto = servicio.split(' (')[0]
                resumen_evento = f"Innova: {nombre_servicio_corto} - {nombre}"
                descripcion_evento = f"Cliente: {nombre}\nTélf: {telefono_limpio}\nEmail: {email}\nNotas: {notas}"
                
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
                    telefono_limpio,
                    email,
                    servicio,
                    notas
                ]
                sheets_manager.agregar_reserva(SPREADSHEET_ID, datos_sheet)
                
                # 3. Enviar correo electrónico
                email_sender.enviar_confirmacion(
                    destinatario=email,
                    nombre_cliente=nombre,
                    servicio=nombre_servicio_corto,
                    fecha=str(fecha),
                    hora=hora.strftime("%I:%M %p")
                )
                
                # Mensaje de confirmación VIP en pantalla
                st.balloons()
                st.success("🎉 ¡Tu cita ha sido agendada con éxito!")
                st.markdown(f"""
                <div style="background-color: #1A2218; border: 1px solid #2E7D32; padding: 15px; border-radius: 8px; margin-top: 10px;">
                    <p style="margin:0; color: #81C784;"><b>Resumen de Reserva:</b></p>
                    <p style="margin:5px 0 0 0;">📌 <b>Servicio:</b> {nombre_servicio_corto}<br>
                    📅 <b>Fecha:</b> {fecha}<br>
                    ⏰ <b>Hora:</b> {hora.strftime('%I:%M %p')}<br>
                    📍 <b>Lugar:</b> Av. Francia, C.C. Divina Pastora</p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error al procesar la solicitud: {e}")
