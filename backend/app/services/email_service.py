import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings

class EmailService:
    async def send_email(self, to_email: str, subject: str, content: str):
        """Sends an email using SMTP."""
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            print(f"SMTP credentials not set. Mocking email to {to_email}")
            print(f"Subject: {subject}")
            print(f"Content: {content}")
            return True

        message = EmailMessage()
        message["From"] = settings.SMTP_FROM or settings.SMTP_USER
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(content)

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_SERVER,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=False,
                start_tls=True,
            )
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    async def send_appointment_confirmation(self, patient_email: str, patient_name: str, appt_time: str, doctor_name: str, calendar_link: str = None):
        """Helper to send a formatted appointment confirmation."""
        subject = f"Appointment Confirmation: {doctor_name}"
        content = f"Hello {patient_name},\n\nYour appointment with {doctor_name} has been successfully booked for {appt_time}.\n"
        
        if calendar_link:
            content += f"\nYou can add this to your calendar here: {calendar_link}\n"
        
        content += "\nThank you for choosing our clinic!"
        
        return await self.send_email(patient_email, subject, content)

email_service = EmailService()
