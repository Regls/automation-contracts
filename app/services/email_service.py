import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config.settings import settings

async def send_notification_email(client: aiosmtplib.SMTP, to_email: str, recipient_name: str, sign_url: str) -> bool:
    """Send an email notification to the user with the signing link"""

    sender_email = "contato@albertoetadeu.com"

    msg = MIMEMultipart("alternative")
    msg["From"] = f"Alberto & Tadeu Advogados <{sender_email}>"
    msg["To"] = to_email
    msg["Subject"] = "Assinatura Pendente: Contrato de Prestação de Serviços - Alberto & Tadeu Advogados"

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #1a365d;">Olá, {recipient_name}!</h2>
        <p>O seu contrato de prestação de serviços tecnológicos já foi gerado e está pronto para assinatura digital.</p>
        <p>Por favor, clique no link abaixo para visualizar o documento e realizar a sua assinatura de forma segura:</p>
        <p style="margin: 25px 0;">
          <a href="{sign_url}" style="background-color: #2b6cb0; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">
            Visualizar e Assinar Contrato
          </a>
        </p>
        <p style="font-size: 12px; color: #718096;">Se o botão não funcionar, copie e cole este link no seu navegador: {sign_url}</p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin-top: 30px;">
        <p style="font-size: 13px; font-weight: bold;">Alberto & Tadeu Advogados Associados</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_content, "html"))
    print(f"📧 [EMAIL] Preparing to send email to: {to_email}")

    try:
        await client.send_message(msg)
        print(f"✅ [EMAIL] Email sent successfully to: {to_email}")
        return True
    except Exception as e:
        print(f"❌ [EMAIL] Error sending email via SMTP: {e}")
        return False