import asyncio
from supabase import create_async_client, AsyncClient
from app.config.settings import settings
from app.services.pdf_service import generate_contract_pdf

async def handle_pdf_pipeline(name: str, email: str, number: str, address: str):
    """Worker that runs outside the websocket thread"""
    try:
        await asyncio.sleep(0.5)
        output_file = generate_contract_pdf(name, email, number, address)
        print(f"📄 [PIPELINE] PDF generated: ./contratos/{output_file}")
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