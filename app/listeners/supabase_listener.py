import asyncio
import aiosmtplib
from supabase import create_async_client, AsyncClient
from app.config.settings import settings
from app.services.pdf_service import generate_contract_pdf
from app.services.zapsign_service import send_contract_to_zapsign
from app.services.email_service import send_notification_email

EMAIL_QUEUE = asyncio.Queue()

async def email_consumer_worker(queue: asyncio.Queue):
    """Consumer that works the queue in parelism with Mailtrap"""
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
            # Informa à fila que a tarefa atual foi concluída
            queue.task_done()

async def handle_pdf_pipeline(name: str, email: str, number: str, address: str):
    """Worker that runs outside the websocket thread"""
    try:
        await asyncio.sleep(0.5)
        output_file = generate_contract_pdf(name, email, number, address)
        print(f"📄 [PIPELINE] PDF generated: ./contratos/{output_file}")

        zapsign_doc = send_contract_to_zapsign(
            file_path=output_file,
            client_name=name,
            client_email=email
        )

        signers = zapsign_doc.get("signers", [])
        print(f"✨ [PIPELINE] ZapSign generated {len(signers)} links to {name}.")

        job_data = {
            "signers": signers,
            "name": name
        }
        await EMAIL_QUEUE.put(job_data)
        print(f"📨 [PIPELINE] E-mails enqueued for {name}.")

    except Exception as e:
        print(f"❌ [Error PIPELINE]: {e}")

def on_database_insert(payload):
    """Callback triggered automatically via Websocket when a new row is inserted into the table"""
    record = payload["data"].get("record", {})
    if not record:
        return

    name = record.get("name")
    print(f"\n✅ [EVENT] New entry detected: {name}")

    asyncio.ensure_future(
        handle_pdf_pipeline(
            name=name,
            email=record.get("email"),
            number=record.get("number"),
            address=record.get("address")
        )
    )

async def realtime_listener():
    settings.validate()

    asyncio.create_task(email_consumer_worker(EMAIL_QUEUE))

    supabase: AsyncClient = await create_async_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    )

    channel = supabase.channel("realtime_forms_channel")
    channel.on_postgres_changes(
        "INSERT",
        on_database_insert,
        table="response-forms1",
        schema="public",
    )

    def on_subscribe(status, err):
        status_str = str(status)

        if "SUBSCRIBED" in status_str:
            status_custom = "✅ SUBSCRIBED"
        elif "CHANNEL_TIMEOUT" in status_str:
            status_custom = "❌ CHANNEL_TIMEOUT"
        else:
            status_custom = f"⚠️ {status_str}"

        print(f"📡 [REALTIME]: {status_custom} | error: {err}")
        if hasattr(channel, 'postgres_changes_callbacks'):
            for cb in channel.postgres_changes_callbacks:
                print(f"   binding id={cb.id} | event={cb.event} | schema={cb.schema} | table={cb.table}")

    await channel.subscribe(callback=on_subscribe)

    print("⏳ Stabilizing Websocket connection...")
    await asyncio.sleep(2)
    channel_str = str(channel.state)
    if "JOINED" in channel_str:
        channel_custom = "✅ JOINED"
        print(f"🔌 Channel state: {channel_custom}")
    else:
        channel_custom = f"⚠️ {channel_str}"
        print(f"🔌 Channel state: {channel_custom}")

    try:
        while True:  
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("\nStopping the listener...")
    finally:
        print("Stopped listening. Cleaning up resources...")
        await supabase.remove_channel(channel)
        print("Disconnected.")