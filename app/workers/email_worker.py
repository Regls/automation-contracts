import asyncio
import aiosmtplib
from app.config.settings import settings
from app.services.email_service import send_notification_email


async def email_consumer_worker(queue: asyncio.Queue):
    """Consumer that processese emails from the queue respecting rate limit"""
    print("👷 [WORKER] E-mail consumer initializing and waiting for tasks...")

    while True:
        email_job = await queue.get()
        signers = email_job.get("signers")
        client_name = email_job.get("name")

        print(f"\n📧 [QUEUE] Processing e-mails for {client_name}")
        try:
            async with aiosmtplib.SMTP(
                hostname=settings.MAILTRAP_HOST,
                port=settings.MAILTRAP_PORT,
                use_tls=False
            ) as server:
                await server.login(settings.MAILTRAP_USER, settings.MAILTRAP_PASSWORD)

                for index, signer in enumerate(signers):
                    signer_name = signer.get("name")
                    sign_url = signer.get("sign_url")
                    signer_email = signer.get("email")
                    
                    print(f"   👤 Sending to: {signer_name} ➔  {signer_email}")
                    
                    await send_notification_email(
                        client=server,
                        to_email=signer_email,
                        recipient_name=signer_name,
                        sign_url=sign_url
                    )
                    
                    if index < len(signers) - 1:
                        print("⏳ [QUEUE] Waiting 12s to avoid Mailtrap ratelimit...")
                        await asyncio.sleep(12)
            print(f"🎉 [QUEUE] Batch for {client_name} completed sucessfully!")
            # Check if there are more jobs waiting in the queue
            if queue.qsize() > 0:
                print(f"⏳ [QUEUE] {queue.qsize()} task(s) remaining. Waiting 15s for server cooldown...")
                await asyncio.sleep(15)
            
        except Exception as e:
            print(f"❌ [QUEUE] Critical error in SMTP worker: {e}")
        finally:
            queue.task_done()