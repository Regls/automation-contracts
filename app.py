import os
import requests
import asyncio
from dotenv import load_dotenv
from supabase import create_async_client, AsyncClient
from fpdf import FPDF

load_dotenv()

# supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# zapsign configuration
ZAPSIGN_URL = "https://sandbox.api.zapsign.com.br/api/v1/"
ZAPSIGN_API_TOKEN = os.getenv("ZAPSIGN_API_TOKEN")

class GenerateContract(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, "Contrato de Prestação de Serviços", align="C")
        self.ln(10)

def generate_pdf_locally(name, email, number, address):
    """Generate a PDF contract locally with the provided user data"""
    pdf = GenerateContract()
    pdf.add_page()
    pdf.set_font('Helvetica', size=11)

    texto_contrato = (
        f"Pelo presente instrumento, de um lado o Prestador, e de outro lado o Sr(a). {name}, "
        f"portador do e-mail {email}, telefone {number} e residente no endereço {address}, "
        "estabelecem o presente contrato de prestação de serviços tecnológicos..."
    )

    pdf.multi_cell(0, 10, text=texto_contrato)

    safe_name = name.replace(" ", "_").replace("/", "_").replace("\\", "-")
    output_path = f"contratos/contrato_{safe_name}.pdf"

    pdf.output(output_path)
    return output_path

async def run_pdf_generation(name, email, number, address):
    """Worker that runs outside the websocket thread"""
    try:
        await asyncio.sleep(0.5)
        output_file = generate_pdf_locally(name, email, number, address)
        print(f"📄 PDF generated: ./contratos/{output_file}")
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")

# 🎯 O PULO DO GATO DEFINITIVO:
# O callback precisa ser síncrono para o Realtime chamar sem dar 'never awaited'
def process_new_entry(payload):
    """Callback triggered automatically via Websocket when a new row is inserted into the table"""
    new_row = payload["data"].get("record", {})
    if not new_row:
        return

    name = new_row.get("name")
    email = new_row.get("email")
    number = new_row.get("number")
    address = new_row.get("address")

    print(f"\n✅ New entry detected: {name}")
    asyncio.ensure_future(run_pdf_generation(name, email, number, address))

async def listen_database():
    # Voltamos para o cliente assíncrono oficial
    supabase: AsyncClient = await create_async_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    channel = supabase.channel("realtime_forms_channel")

    channel.on_postgres_changes(
        "INSERT",
        process_new_entry,
        table="response-forms1",
        schema="public",
    )
    def on_subscribe(status, err):
        print(f"📡 Subscription status: {status} | error: {err}")
        if hasattr(channel, 'postgres_changes_callbacks'):
            for cb in channel.postgres_changes_callbacks:
                print(f"   binding id={cb.id} | event={cb.event} | schema={cb.schema} | table={cb.table}")

    await channel.subscribe(callback=on_subscribe)

    print("⏳ Stabilizing Websocket connection...")
    await asyncio.sleep(2)
    print(f"🔌 Channel state: {channel.state}")

    try:
        while True:  
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("\nStopping the listener...")
    finally:
        print("Stopped listening. Cleaning up resources...")
        await supabase.remove_channel(channel)
        print("Disconnected.")

if __name__ == "__main__":
    try:
        # Usa o asyncio normal
        asyncio.run(listen_database())
    except KeyboardInterrupt:
        print("\nApplication interrupted by developer.")