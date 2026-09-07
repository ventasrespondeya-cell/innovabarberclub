import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSender:
    def __init__(self, remitente_email, contraseña_app):
        self.remitente = remitente_email
        self.contraseña = contraseña_app  # Contraseña de aplicación de Gmail

    def enviar_confirmacion(self, destinatario, nombre_cliente, servicio, fecha, hora):
        """
        Envía un correo de confirmación de reserva al cliente.
        """
        asunto = f"Confirmación de Reserva - {servicio}"
        
        cuerpo = f"""
        ¡Hola {nombre_cliente}!

        Tu cita ha sido reservada con éxito. Aquí tienes los detalles:

        - Servicio: {servicio}
        - Fecha: {fecha}
        - Hora: {hora}

        ¡Te esperamos! Si necesitas cancelar o reprogramar, por favor contáctanos con anticipación.
        """

        mensaje = MIMEMultipart()
        mensaje['From'] = self.remitente
        mensaje['To'] = destinatario
        mensaje['Subject'] = asunto
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        try:
            # Conexión al servidor SMTP de Gmail
            servidor = smtplib.SMTP('smtp.gmail.com', 587)
            servidor.starttls()
            servidor.login(self.remitente, self.contraseña)
            servidor.sendmail(self.remitente, destinatario, mensaje.as_string())
            servidor.quit()
            return True
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            return False