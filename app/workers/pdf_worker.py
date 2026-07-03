import asyncio
from app.services import generate_contract_pdf, send_contract_to_zapsign, send_whatsapp_notification
from app.queue import EMAIL_QUEUE


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

        client_sign_url = None
        for signer in signers:
            if signer.get("email") == email:
                client_sign_url = signer.get("sign_url")
                break
        
        if client_sign_url and number:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                send_whatsapp_notification,
                number,
                name,
                client_sign_url
            )
        else:
            print("⚠️ [PIPELINE] Could not send WhatsApp: client link or phone number missing.")

        job_data = {
            "signers": signers,
            "name": name
        }
        await EMAIL_QUEUE.put(job_data)
        print(f"📨 [PIPELINE] E-mails enqueued for {name}.")

    except Exception as e:
        print(f"❌ [Error PIPELINE]: {e}")